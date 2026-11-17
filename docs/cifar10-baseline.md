# CIFAR-10 laptop baseline

This benchmark uses the [MLPerf Tiny ResNet-8 reference](https://github.com/mlcommons/tiny/tree/4addd0fa08d216e20637637874e084895f289da4/benchmark/training/image_classification) and the [official CIFAR-10 test split](https://cave.cs.toronto.edu/kriz/cifar.html). The reference model is the published float32 TFLite file. The test split contains 10,000 RGB images at 32 × 32 pixels, with 1,000 images per class.

## Set up the model and test data

Run these commands from the project folder in PowerShell. The setup was verified with 64-bit Python 3.14 on Windows.

```powershell
python -m venv runs/cifar10-baseline/venv
.\runs\cifar10-baseline\venv\Scripts\python.exe -m pip install -r ml/requirements-cifar10.txt
.\runs\cifar10-baseline\venv\Scripts\python.exe ml/cifar10_inputs.py
```

Setup downloads the model and the CIFAR-10 archive, checks their SHA-256 hashes, verifies the model's input and output shapes, and loads the full test split. The assets are stored locally under `runs/cifar10-baseline/assets/`.

## Run the benchmark

```powershell
.\runs\cifar10-baseline\venv\Scripts\python.exe ml/benchmark_cifar10.py |
    Tee-Object -FilePath runs/cifar10-baseline/laptop-run.json
```

The script passes raw RGB values from 0 to 255 to the model as float32, matching the [upstream test](https://github.com/mlcommons/tiny/blob/4addd0fa08d216e20637637874e084895f289da4/benchmark/training/image_classification/tflite_test.py). It warms up with 200 images, then processes the entire official test split again, one image at a time. The JSON includes source hashes, runtime versions, accuracy, and latency percentiles.

## Laptop results

**87.19% top-1 accuracy (8,719 of 10,000)** in all three runs on an Intel Core Ultra 7 155H laptop running Windows 11. This clears the [MLPerf Tiny quality target](https://mlcommons.org/benchmarks/inference-tiny/) of 85%. The runtime was LiteRT 2.3.0 with the XNNPACK CPU delegate, one thread, and batch size one.

| Run | Accuracy | Inference median | Inference p95 | Host median | Host p95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 87.19% | 0.654 ms | 1.076 ms | 0.663 ms | 1.105 ms |
| 2 | 87.19% | 0.648 ms | 1.009 ms | 0.656 ms | 1.038 ms |
| 3 | 87.19% | 0.654 ms | 0.969 ms | 0.662 ms | 0.993 ms |

Inference timing covers the runtime's `invoke()` call. Host timing starts with an image already prepared in memory and includes copying it into the runtime, running inference, reading the scores, and choosing the top class. The p95 is the time that 95% of images finished within. These measurements establish the laptop baseline for the integer model and FPGA build.
