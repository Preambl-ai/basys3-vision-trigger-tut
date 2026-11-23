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

## INT8 comparison

The integer run uses the [published quantized ResNet-8](https://github.com/mlcommons/tiny/blob/4addd0fa08d216e20637637874e084895f289da4/benchmark/training/image_classification/trained_models/pretrainedResnet_quant.tflite) from the same upstream revision. It subtracts 128 from each RGB byte to get the signed input expected by the model. The test split, CPU thread count, batch size, and warmup match the float32 run.

```powershell
.\runs\cifar10-baseline\venv\Scripts\python.exe ml/benchmark_cifar10.py --int8
.\runs\cifar10-baseline\venv\Scripts\python.exe ml/benchmark_cifar10.py --int8 --reference-kernels
```

The optimized LiteRT CPU path got **86.97% top-1 (8,697 of 10,000)** in all four runs. That is **0.22 percentage points** below float32 and above the 85% target. Median inference took **0.216–0.226 ms**, and p95 took **0.297–0.336 ms**.

The built-in LiteRT reference kernels got **87.07% top-1 (8,707 of 10,000)** on the full test set. This is the accuracy reference for an FPGA implementation that matches their integer arithmetic.

### Reference vectors for the FPGA

The first command also writes `runs/cifar10-baseline/int8-reference.npz`. It uses LiteRT's built-in reference kernels to generate the expected scores for the first two official test images of each class, selected by label and dataset order. The archive stores the signed 32 × 32 RGB inputs, all ten raw signed output scores per image, the classes with the highest score, the original test indices and labels, and the model and dataset hashes. Class ties use the lowest class index.

The reference kernels and the optimized CPU path agreed on **19 of 20 top classes** and **10 of 20 exact score vectors** for these images. Use the built-in reference scores to check the hardware implementation. The optimized CPU path provides the laptop speed baseline.

## Fresh comparison run — November 23, 2026

I reran both optimized models after the compact-model training finished. Accuracy remained **87.19% float32** and **86.97% INT8** on all 10,000 test images. Median core inference was **0.4826 ms float32** and **0.1780 ms INT8** in these fresh single runs. Timing varies with system conditions; the original repeated measurements above remain the historical baseline.

[Fresh float32 JSON](benchmarks/resnet8-float32-current.json) · [Fresh INT8 JSON](benchmarks/resnet8-int8-current.json) · [Compact-model comparison](compact-cifar10.md)
