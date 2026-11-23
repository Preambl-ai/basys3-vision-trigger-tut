# Compact CIFAR-10 experiment

I added a smaller classifier to test whether reducing the model's work makes it a better candidate for the Basys 3. This is a CPU training and benchmarking experiment. The model has not been implemented on the FPGA.

## What I changed

- I preserved the existing float32 and INT8 ResNet-8 measurements as JSON files in `docs/benchmarks/`.
- I added a comparison script that checks full-test accuracy counts and timing percentiles before generating a table.
- I added a six-convolution CNN with 8, 16, and 32 channels. It uses RGB images at 32 × 32 pixels and predicts the ten CIFAR-10 categories. This is a fixed-category classifier, not an arbitrary-image recognition system.
- I separated the official 50,000 training images into 45,000 training and 5,000 validation images, with equal class proportions and a recorded seed. The official 10,000 test images are kept separate.
- I select the checkpoint using validation accuracy. Only training images receive random crops and flips.
- I added static INT8 conversion with 500 balanced calibration images from the training partition. Validation and test images are excluded from calibration.

The model is trained from scratch as a compact baseline. This does not establish that custom training is better than pretrained models, pruning, or distillation. Those are later comparisons.

## Measured result — November 23, 2026

I completed the planned 20 epochs with seed 42. Training took about 15.5 minutes on the CPU. Epoch 20 had the best validation accuracy, **76.10%**, so that checkpoint was selected before evaluating the official test set.

| Model | Test accuracy | Core median, run 1 | Core median, run 2 | Kernel weight bytes |
| --- | ---: | ---: | ---: | ---: |
| ResNet-8 float32, fresh reference run | 87.19% | 0.4826 ms | — | 309,440 |
| ResNet-8 INT8, fresh reference run | 86.97% | 0.1780 ms | — | 77,360 |
| Compact CNN float32 | 75.74% | 0.5302 ms | 0.5462 ms | 73,568 |
| Compact CNN INT8 | 75.48% | 0.5531 ms | 0.4208 ms | 18,392 |

Both compact runs produced identical full-test scores within each precision: **7,574/10,000 correct** for float32 and **7,548/10,000** for INT8. Quantization cost **0.26 percentage points** of test accuracy. I verified that calibration indices belonged only to the training partition, export hashes matched the saved files, and reference vectors matched the recorded predictions.

The compact architecture uses **2,580,800 dense MACs** and **18,392 kernel parameters**, versus ResNet-8's **12,501,632 MACs** and **77,360 kernel parameters**. That is about **79% fewer dense products** and **76% fewer kernel weights**. Kernel storage excludes biases, quantization metadata, and hardware packing. Serialized export sizes are listed separately in the model manifest.

**This candidate does not pass the 85% accuracy requirement.** It also did not beat optimized INT8 ResNet-8's CPU latency in these implementations. Smaller counts did not produce a better overall result. INT8 timing varied between runs; raw p95/p99 values are available, and these interactive-laptop timings are not controlled deployment measurements. No FPGA speedup or energy saving has been demonstrated.

I would keep ResNet-8 as the accuracy reference and use validation data to investigate a stronger compact architecture, a longer training schedule, or structural pruning. This single limited-budget run does not establish the best accuracy this architecture could ever achieve. The official test results are now observed and must not become the tuning objective.

### Saved proof

- [Training settings](benchmarks/compact-cifar10/training/config.json), [history](benchmarks/compact-cifar10/training/history.json), [summary](benchmarks/compact-cifar10/training/summary.json), [split indices](benchmarks/compact-cifar10/training/split.npz), and [installed versions](benchmarks/compact-cifar10/training/environment.txt).
- [Float32 result](benchmarks/compact-cifar10/float32.json) and [repeat](benchmarks/compact-cifar10/float32-repeat-2.json); [INT8 result](benchmarks/compact-cifar10/int8.json) and [repeat](benchmarks/compact-cifar10/int8-repeat-2.json).
- [Full float predictions and timings](benchmarks/compact-cifar10/float32-predictions.npz) and [full INT8 predictions and timings](benchmarks/compact-cifar10/int8-predictions.npz). The folder also includes both repeat-run arrays and the 20-image regression references.
- [Trained checkpoint, CPU exports, hashes, and replay instructions](../models/compact-cifar10/README.md).
- [Generated comparison with fresh reference measurements](benchmarks/comparison.md).

## Set up

Run from the repository root in PowerShell. A short environment path avoids Windows package installation path-length errors. This leaves the existing environments alone.

```powershell
python -m venv "$env:USERPROFILE/.venvs/preambl-compact"
$compactPython = "$env:USERPROFILE/.venvs/preambl-compact/Scripts/python.exe"
& $compactPython -m pip install -r ml/requirements-compact.txt
& $compactPython ml/test_compact.py
```

## Train

```powershell
& $compactPython ml/train_compact.py --epochs 20 --seed 42 --threads 4 --output runs/compact-cifar10/seed-42
```

The script refuses to overwrite an existing run. Choose a new directory for another experiment. It saves the settings, exact split indices, per-epoch history, and best checkpoint. Training uses the CPU; no Basys 3 is needed. The initial budget is 20 epochs and one seed. It is an initial candidate, not an exhaustive architecture search.

## Export and measure

Freeze the checkpoint and training choices before running the official test evaluation:

```powershell
& $compactPython ml/benchmark_compact.py runs/compact-cifar10/seed-42/best.pt --output runs/compact-cifar10/float32
& $compactPython ml/benchmark_compact.py runs/compact-cifar10/seed-42/best.pt --int8 --output runs/compact-cifar10/int8
& $compactPython ml/compare_models.py docs/benchmarks/resnet8-float32.json docs/benchmarks/resnet8-int8.json runs/compact-cifar10/float32/result.json runs/compact-cifar10/int8/result.json --output runs/compact-cifar10/comparison.md
```

Both compact versions fold batch normalization into the convolutions and run a saved/reloaded TorchScript artifact. INT8 conversion checks that all six convolutions and the classifier use signed 8-bit kernel weights. Activations use unsigned 8-bit values; input and returned logits are float32. This is CPU quantization, not a complete FPGA arithmetic implementation.

The verified Windows PyTorch build exposes the `onednn` quantized engine. The script explicitly selects it and records that choice. It fails clearly if that backend is unavailable.

Each benchmark warms up on 200 images and then measures all 10,000 test images, batch one, one CPU thread. Core timing covers the model forward call. Host timing adds copying an already prepared input and selecting the top class. Image decoding, preprocessing, camera capture, and serial transfers are excluded. Per-image predictions and timings stay in the local run directory for inspection.

ResNet-8 uses LiteRT/XNNPACK; the compact candidate uses PyTorch/TorchScript. Timings compare these implementations, not architectures under an identical runtime. Historical baseline measurements were also taken on a different date. Repeat measurements on an idle machine before making a speed claim.

The exported reference archive contains 20 fixed test inputs and CPU output scores. These can check export regressions. They are not a specification of bit-exact FPGA accumulators, rounding, or rescaling; that needs a later integer reference and RTL verification.

## How I judge the result

The existing minimum accuracy target remains **85%**. A small model that falls below it is a useful experiment, but does not pass the prototype's quality requirement. Fewer weights or MACs alone do not demonstrate speed, power savings, or FPGA timing closure.

Next, I would compare a stronger compact candidate or a pruned model using validation data, then check FPGA resources for a candidate that meets the quality requirement. Further tuning should keep the test set out of model selection; the test results published here are already observed.

## Implementation references

- [PyTorch static quantization and fusion APIs](https://docs.pytorch.org/docs/2.9/quantization-support.html)
- [PyTorch reproducibility guidance](https://docs.pytorch.org/docs/2.9/notes/randomness.html)
- [Official CIFAR-10 dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

PyTorch's `torch.ao.quantization` and TorchScript APIs are legacy/deprecated APIs in newer releases. This experiment pins PyTorch 2.9.0 for reproducibility; a production toolchain should evaluate maintained export and quantization paths separately.
