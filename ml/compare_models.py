"""Combine measured CIFAR-10 result files into a readable comparison."""

import argparse
import json
import math
from pathlib import Path


def read_result(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8-sig"))
    count = result["test_images"]
    correct = result["top1_correct"]
    if count != 10_000 or not 0 <= correct <= count:
        raise ValueError(f"{path}: expected the full 10,000-image test set")
    accuracy = 100 * correct / count
    if not math.isclose(accuracy, result["top1_percent"], abs_tol=1e-6):
        raise ValueError(f"{path}: accuracy does not match the correct count")
    if result["batch_size"] != 1 or result["cpu_threads"] != 1:
        raise ValueError(f"{path}: comparison requires batch one and one CPU thread")
    for field in ("inference_ms", "host_classification_ms"):
        values = [result[field][key] for key in ("median", "p95", "p99")]
        if not all(math.isfinite(x) and x > 0 for x in values) or values != sorted(values):
            raise ValueError(f"{path}: invalid {field} percentiles")
    return result


def make_report(paths: list[Path]) -> str:
    results = [read_result(path) for path in paths]
    if len({r["dataset_sha256"] for r in results}) != 1:
        raise ValueError("Result files use different datasets")
    lines = [
        "# CIFAR-10 model comparison", "",
        "Measured CPU results: 10,000 official test images, batch one, one CPU thread.",
        "Runtime, date, and machine differences can affect timings. These are not FPGA measurements.", "",
        "| Model | Runtime | Accuracy | Core median (ms) | Core p95 (ms) | Host median (ms) | Dense MACs | Kernel parameters | Kernel weight bytes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in results:
        runtime = r.get("runtime", f"LiteRT {r.get('litert', '?')}")
        resource = r.get("resources", {})
        lines.append(
            f"| {r['model']} | {runtime} | {r['top1_percent']:.2f}% | "
            f"{r['inference_ms']['median']:.4f} | {r['inference_ms']['p95']:.4f} | "
            f"{r['host_classification_ms']['median']:.4f} | "
            f"{resource.get('dense_macs_per_image', 'unreported')} | "
            f"{resource.get('kernel_parameters', 'unreported')} | "
            f"{resource.get('kernel_weight_bytes', 'unreported')} |"
        )
    lines.extend(["", "MAC counts cover convolution and linear products, including padded taps;",
                  "they exclude pooling, activation, rescaling, and data movement.",
                  "Kernel bytes exclude biases, scales, metadata, and FPGA packing overhead.",
                  "Missing resource data is shown as unreported, never as zero.", "", "## Source results", ""])
    for path, r in zip(paths, results):
        lines.append(f"- `{path.as_posix()}` — model SHA-256 `{r['model_sha256']}`")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = make_report(args.results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
