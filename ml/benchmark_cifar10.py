"""Measure batch-one CPU inference for the MLPerf Tiny ResNet-8 models."""

import argparse
import json
import platform
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from tempfile import NamedTemporaryFile
from time import perf_counter_ns

import numpy as np

from cifar10_inputs import (
    CLASS_COUNT,
    DATASET_SHA256,
    IMAGE_SHAPE,
    INT8_INPUT_QUANTIZATION,
    INT8_MODEL_SHA256,
    INT8_OUTPUT_QUANTIZATION,
    MLPERF_REVISION,
    MODEL_SHA256,
    load_test_set,
    open_reference_model,
)

WARMUP_IMAGES = 200
REFERENCE_VECTORS = Path("runs/cifar10-baseline/int8-reference.npz")


def latency_ms(samples_ns: np.ndarray) -> dict[str, float]:
    median, p95, p99 = np.percentile(samples_ns, [50, 95, 99]) / 1_000_000
    return {"median": float(median), "p95": float(p95), "p99": float(p99)}


def save_int8_reference(
    inputs: np.ndarray, labels: np.ndarray, cpu_scores: np.ndarray
) -> dict[str, str | int]:
    # Select the first two official test images of each class before checking predictions.
    indices = np.concatenate([np.flatnonzero(labels == label)[:2] for label in range(CLASS_COUNT)])
    interpreter, input_index, output_index = open_reference_model(int8=True, reference_kernels=True)
    inputs_int8 = inputs[indices, 0]
    scores_int8 = np.empty((len(indices), CLASS_COUNT), dtype=np.int8)
    for row, image in enumerate(inputs_int8):
        interpreter.set_tensor(input_index, image[None, ...])
        interpreter.invoke()
        scores_int8[row] = interpreter.get_tensor(output_index)[0]
    expected_classes = scores_int8.argmax(axis=1)

    temporary = NamedTemporaryFile(dir=REFERENCE_VECTORS.parent, delete=False)
    pending = Path(temporary.name)
    try:
        with temporary:
            np.savez_compressed(
                temporary,
                test_indices=indices,
                true_classes=labels[indices],
                inputs_int8=inputs_int8,
                scores_int8=scores_int8,
                expected_classes=expected_classes,
                model_sha256=INT8_MODEL_SHA256,
                dataset_sha256=DATASET_SHA256,
            )
        pending.replace(REFERENCE_VECTORS)
    finally:
        pending.unlink(missing_ok=True)

    return {
        "path": REFERENCE_VECTORS.as_posix(),
        "images": len(indices),
        "classes_matching_cpu_delegate": int(
            np.count_nonzero(expected_classes == cpu_scores[indices].argmax(axis=1))
        ),
        "score_vectors_matching_cpu_delegate": int(
            np.count_nonzero(np.all(scores_int8 == cpu_scores[indices], axis=1))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--int8", action="store_true", help="benchmark the integer model and save reference vectors")
    parser.add_argument("--reference-kernels", action="store_true", help="evaluate INT8 with the LiteRT reference kernels")
    args = parser.parse_args()
    if args.reference_kernels and not args.int8:
        parser.error("--reference-kernels requires --int8")

    images, labels = load_test_set()
    interpreter, input_index, output_index = open_reference_model(
        int8=args.int8, reference_kernels=args.reference_kernels
    )
    # Match the upstream test: raw RGB for float, or RGB minus 128 for int8.
    if args.int8:
        inputs = (images.astype(np.int16) - 128).astype(np.int8)
    else:
        inputs = images.astype(np.float32)
    inputs = inputs.reshape(-1, 1, *IMAGE_SHAPE)
    for image in inputs[:WARMUP_IMAGES]:
        interpreter.set_tensor(input_index, image)
        interpreter.invoke()
        interpreter.get_tensor(output_index)

    predictions = np.empty_like(labels)
    int8_scores = None
    if args.int8 and not args.reference_kernels:
        int8_scores = np.empty((len(inputs), CLASS_COUNT), dtype=np.int8)
    inference_ns = np.empty(len(inputs), dtype=np.int64)
    host_ns = np.empty_like(inference_ns)
    for index, image in enumerate(inputs):
        host_start = perf_counter_ns()
        interpreter.set_tensor(input_index, image)
        inference_start = perf_counter_ns()
        interpreter.invoke()
        inference_end = perf_counter_ns()
        scores = interpreter.get_tensor(output_index)
        predictions[index] = scores.argmax()
        host_end = perf_counter_ns()
        if not np.isfinite(scores).all():
            raise ValueError(f"Non-finite model scores for test image {index}")
        if int8_scores is not None:
            int8_scores[index] = scores[0]
        inference_ns[index] = inference_end - inference_start
        host_ns[index] = host_end - host_start

    correct = int(np.count_nonzero(predictions == labels))
    result = {
        "model": "MLPerf Tiny ResNet-8 int8" if args.int8 else "MLPerf Tiny ResNet-8 float32",
        "model_revision": MLPERF_REVISION,
        "model_sha256": INT8_MODEL_SHA256 if args.int8 else MODEL_SHA256,
        "dataset": "CIFAR-10 official test split",
        "dataset_sha256": DATASET_SHA256,
        "test_images": len(labels),
        "top1_correct": correct,
        "top1_percent": 100 * correct / len(labels),
        "batch_size": 1,
        "cpu_threads": 1,
        "cpu_kernels": "LiteRT reference" if args.reference_kernels else "LiteRT default",
        "warmup_images": WARMUP_IMAGES,
        "inference_ms": latency_ms(inference_ns),
        "host_classification_ms": latency_ms(host_ns),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "measured_at_utc": datetime.now(timezone.utc).isoformat(),
        "runtime": f"LiteRT {version('ai-edge-litert')} CPU",
        "litert": version("ai-edge-litert"),
        "numpy": np.__version__,
    }
    if args.int8:
        input_scale, input_zero_point = INT8_INPUT_QUANTIZATION
        output_scale, output_zero_point = INT8_OUTPUT_QUANTIZATION
        result["input_quantization"] = {"scale": input_scale, "zero_point": input_zero_point}
        result["output_quantization"] = {"scale": output_scale, "zero_point": output_zero_point}
        if int8_scores is not None:
            result["reference_vectors"] = save_int8_reference(inputs, labels, int8_scores)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
