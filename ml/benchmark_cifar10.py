"""Measure batch-one CPU inference for the MLPerf Tiny float32 model."""

import json
import platform
from importlib.metadata import version
from time import perf_counter_ns

import numpy as np

from cifar10_inputs import (
    DATASET_SHA256,
    IMAGE_SHAPE,
    MLPERF_REVISION,
    MODEL_SHA256,
    load_test_set,
    open_reference_model,
)

WARMUP_IMAGES = 200


def latency_ms(samples_ns: np.ndarray) -> dict[str, float]:
    median, p95, p99 = np.percentile(samples_ns, [50, 95, 99]) / 1_000_000
    return {"median": float(median), "p95": float(p95), "p99": float(p99)}


def main() -> None:
    images, labels = load_test_set()
    interpreter, input_index, output_index = open_reference_model()
    # Match the upstream float model's raw 0–255 RGB input.
    inputs = images.astype(np.float32).reshape(-1, 1, *IMAGE_SHAPE)
    for image in inputs[:WARMUP_IMAGES]:
        interpreter.set_tensor(input_index, image)
        interpreter.invoke()
        interpreter.get_tensor(output_index)

    predictions = np.empty_like(labels)
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
        inference_ns[index] = inference_end - inference_start
        host_ns[index] = host_end - host_start

    correct = int(np.count_nonzero(predictions == labels))
    result = {
        "model": "MLPerf Tiny ResNet-8 float32",
        "model_revision": MLPERF_REVISION,
        "model_sha256": MODEL_SHA256,
        "dataset": "CIFAR-10 official test split",
        "dataset_sha256": DATASET_SHA256,
        "test_images": len(labels),
        "top1_correct": correct,
        "top1_percent": 100 * correct / len(labels),
        "batch_size": 1,
        "cpu_threads": 1,
        "warmup_images": WARMUP_IMAGES,
        "inference_ms": latency_ms(inference_ns),
        "host_classification_ms": latency_ms(host_ns),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "litert": version("ai-edge-litert"),
        "numpy": np.__version__,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
