"""Pack the published INT8 ResNet-8 weights for a Vivado resource check."""

import argparse
import json
from pathlib import Path

import numpy as np
from ai_edge_litert.interpreter import Interpreter, OpResolverType

from cifar10_inputs import INT8_MODEL_SHA256, MODEL_DIRECTORY_URL, verified_asset

OUTPUT_DIR = Path("build/resnet8-fit")
# Three banks permit a current input, an output, and a residual to be live.
ACTIVATION_BYTES = 3 * 32 * 32 * 16


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lanes", type=int, choices=(32, 64), required=True)
    lanes = parser.parse_args().lanes
    path = verified_asset(
        "resnet8-int8.tflite", f"{MODEL_DIRECTORY_URL}/pretrainedResnet_quant.tflite", INT8_MODEL_SHA256
    )
    interpreter = Interpreter(
        model_path=str(path), experimental_op_resolver_type=OpResolverType.BUILTIN_WITHOUT_DEFAULT_DELEGATES
    )
    interpreter.allocate_tensors()
    tensors = {item["index"]: item for item in interpreter.get_tensor_details()}
    layers = []
    rows = []
    test_taps = []
    test_sums = []
    test_lines = []

    for op in interpreter._get_ops_details():
        kind = op["op_name"]
        if kind not in ("CONV_2D", "FULLY_CONNECTED"):
            continue
        input_index, weight_index, _ = op["inputs"]
        weights = interpreter.get_tensor(weight_index)
        channels = weights.shape[0]
        filters = weights.reshape(channels, -1)
        taps = filters.shape[1]
        output_shape = tensors[op["outputs"][0]]["shape"]
        positions = int(np.prod(output_shape[1:-1]))
        start_row = len(rows)

        for offset in range(0, channels, lanes):
            tile = np.zeros((lanes, taps), dtype=np.int8)
            group = filters[offset : offset + lanes]
            tile[: len(group)] = group
            # The lowest byte in each word supplies lane zero.
            rows.extend(row[::-1].tobytes().hex() for row in tile.T)
        layers.append({
            "operator": int(op["index"]),
            "kind": kind,
            "weight_shape": list(weights.shape),
            "weight_row": start_row,
            "weight_bytes": weights.nbytes,
            "dense_macs": positions * channels * taps,
            "issue_cycles": positions * (len(rows) - start_row),
        })

        if op["index"] in (0, 9):
            # Exercise both a padded 16-lane group and a full 64-channel layer.
            zero_point = int(tensors[input_index]["quantization"][1])
            activations = ((np.arange(taps) * 31) % 256) - 128
            group = filters[:lanes].astype(np.int32)
            sums = np.zeros(lanes, dtype=np.int32)
            sums[: len(group)] = group @ (activations - zero_point)
            test_taps.extend(f"{int(value) & 0xff:02x}" for value in activations)
            test_sums.extend(f"{int(value) & 0xffffffff:08x}" for value in sums)
            test_lines.append(f"{start_row} {taps} {zero_point}")

    if len(layers) != 10 or len(test_lines) != 2:
        raise ValueError("Unexpected ResNet-8 convolution or dense layer layout")
    destination = OUTPUT_DIR / str(lanes)
    destination.mkdir(parents=True, exist_ok=True)
    for filename, lines in (
        ("weights.mem", rows),
        ("dot_inputs.mem", test_taps),
        ("dot_expected.mem", test_sums),
        ("dot_cases.txt", test_lines),
    ):
        (destination / filename).write_text("\n".join(lines) + "\n", encoding="ascii")

    summary = {
        "lanes": lanes,
        "weight_rows": len(rows),
        "weight_bytes": sum(layer["weight_bytes"] for layer in layers),
        "packed_weight_bytes": len(rows) * lanes,
        "activation_bytes": ACTIVATION_BYTES,
        "dense_macs_per_image": sum(layer["dense_macs"] for layer in layers),
        "issue_cycles_per_image": sum(layer["issue_cycles"] for layer in layers),
        "layers": layers,
    }
    (destination / "model.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"{lanes} lanes: {len(rows)} weight rows, {summary['issue_cycles_per_image']:,} issue cycles per image")


if __name__ == "__main__":
    main()
