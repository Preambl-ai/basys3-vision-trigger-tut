"""Export and measure a frozen compact checkpoint, in float32 or static INT8."""

import argparse
import copy
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import torch

from cifar10_inputs import DATASET_SHA256, load_test_set, load_training_set, sha256, training_indices
from compact_model import ARCHITECTURE, CompactCNN, resource_counts
from train_compact import accuracy


def quantize_model(model, calibration):
    if "onednn" not in torch.backends.quantized.supported_engines:
        raise ValueError("This experiment requires PyTorch's oneDNN quantized backend")
    torch.backends.quantized.engine = "onednn"
    prepared = copy.deepcopy(model).eval()
    prepared.fuse()
    prepared.qconfig = torch.ao.quantization.get_default_qconfig("onednn")
    torch.ao.quantization.prepare(prepared, inplace=True)
    with torch.inference_mode():
        for batch in calibration.split(50):
            prepared(batch)
    torch.ao.quantization.convert(prepared, inplace=True)
    quantized = [layer for layer in prepared.modules()
                 if isinstance(layer, (torch.ao.nn.quantized.Conv2d, torch.ao.nn.quantized.Linear))]
    if len(quantized) != 7 or any(layer.weight().dtype != torch.qint8 for layer in quantized):
        raise ValueError("Expected six INT8 convolutions and one INT8 classifier")
    return prepared


def percentiles(samples):
    return dict(zip(("median", "p95", "p99"), (np.percentile(samples, [50, 95, 99]) / 1e6).tolist()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--int8", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        parser.error("output directory must be empty; choose a new benchmark directory")
    torch.set_num_threads(1)
    torch.manual_seed(42)
    saved = torch.load(args.checkpoint, weights_only=True, map_location="cpu")
    if saved["architecture"] != ARCHITECTURE or saved["dataset_sha256"] != DATASET_SHA256:
        raise ValueError("Checkpoint architecture or dataset does not match")
    model = CompactCNN().eval()
    model.load_state_dict(saved["state_dict"])
    resources = resource_counts(model)
    metadata = {}
    if args.int8:
        images, labels = load_training_set()
        train, validation = training_indices(labels, saved["seed"])
        # Balanced, fixed calibration subset from training only; never validation/test.
        indices = np.concatenate([train[labels[train] == label][:50] for label in range(10)])
        calibration = torch.from_numpy(images[indices].transpose(0, 3, 1, 2).copy()).float().div(255)
        model = quantize_model(model, calibration)
        validation_accuracy = accuracy(model,
            torch.from_numpy(images[validation].transpose(0, 3, 1, 2).copy()),
            torch.from_numpy(labels[validation]))
        metadata = {"calibration_training_indices": indices.tolist(),
                    "calibration_images": len(indices), "quantization_backend": "onednn",
                    "quantization": "per-channel signed INT8 kernels; unsigned UINT8 activations; float I/O",
                    "validation_accuracy_percent": validation_accuracy,
                    "input_scale": float(model.quant.scale.item()),
                    "input_zero_point": int(model.quant.zero_point.item()),
                    "output_scale": float(model.classifier.scale),
                    "output_zero_point": int(model.classifier.zero_point)}
        resources["kernel_weight_bytes"] = resources["int8_kernel_weight_bytes"]
    else:
        model.fuse()
    args.output.mkdir(parents=True, exist_ok=True)
    with torch.inference_mode():
        traced = torch.jit.trace(model, torch.zeros(1, 3, 32, 32))
        traced.save(str(args.output / "model.ts"))
        deployed = torch.jit.load(str(args.output / "model.ts")).eval()
        # Confirm serialization preserves outputs on nonzero, varied inputs.
        probe = torch.rand(4, 3, 32, 32)
        torch.testing.assert_close(deployed(probe), model(probe), rtol=0, atol=0)
        images, labels = load_test_set()
        inputs = torch.from_numpy(images.transpose(0, 3, 1, 2).copy()).float().div(255)
        for image in inputs[:200]:
            deployed(image.unsqueeze(0))
        scores = np.empty((len(labels), 10), dtype=np.float32)
        predictions = np.empty(len(labels), dtype=np.int64)
        inference_ns, host_ns = [], []
        for index, image in enumerate(inputs):
            host_start = perf_counter_ns()
            batch = image.unsqueeze(0).clone()
            start = perf_counter_ns()
            output = deployed(batch)
            end = perf_counter_ns()
            predictions[index] = int(output.argmax(1).item())
            host_end = perf_counter_ns()
            scores[index] = output[0].numpy()
            inference_ns.append(end - start)
            host_ns.append(host_end - host_start)
        if not np.isfinite(scores).all():
            raise ValueError("Non-finite output scores")
    selected = np.concatenate([np.flatnonzero(labels == label)[:2] for label in range(10)])
    np.savez_compressed(args.output / "reference.npz", test_indices=selected,
        inputs_rgb_uint8=images[selected], true_classes=labels[selected],
        scores_float32=scores[selected], expected_classes=predictions[selected],
        model_sha256=sha256(args.output / "model.ts"), dataset_sha256=DATASET_SHA256)
    np.savez_compressed(args.output / "test-predictions.npz", true_classes=labels,
                        predicted_classes=predictions, scores_float32=scores,
                        inference_ns=inference_ns, host_ns=host_ns)
    correct = int(np.count_nonzero(predictions == labels))
    result = {"model": f"CompactCNN {'int8' if args.int8 else 'float32'}",
              "architecture": ARCHITECTURE, "model_sha256": sha256(args.output / "model.ts"),
              "checkpoint_sha256": sha256(args.checkpoint), "selected_epoch": saved["epoch"],
              "seed": saved["seed"], "float_validation_percent": saved["validation_accuracy_percent"],
              "dataset": "CIFAR-10 official test split", "dataset_sha256": DATASET_SHA256,
              "test_images": len(labels), "top1_correct": correct, "top1_percent": 100 * correct / len(labels),
              "batch_size": 1, "cpu_threads": 1, "warmup_images": 200,
              "runtime": f"PyTorch {torch.__version__} TorchScript CPU",
              "inference_ms": percentiles(inference_ns), "host_classification_ms": percentiles(host_ns),
              "timing_scope": "core=forward; host=copy prepared float input, forward, argmax; excludes decoding/preprocessing",
              "resources": resources, "torch": torch.__version__, "numpy": np.__version__,
              "python": platform.python_version(), "platform": platform.platform(),
              "processor": platform.processor(), "measured_at_utc": datetime.now(timezone.utc).isoformat(),
              "serialized_model_bytes": (args.output / "model.ts").stat().st_size,
              "quantization_details": metadata,
              "per_class_correct": np.bincount(labels[predictions == labels], minlength=10).tolist(),
              "reference_vectors": {"images": len(selected), "format": "RGB bytes and dequantized float scores; CPU regression reference"}}
    (args.output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"{result['model']}: {correct}/10000 ({result['top1_percent']:.2f}%), "
          f"median {result['inference_ms']['median']:.4f} ms; saved {args.output}")


if __name__ == "__main__":
    main()
