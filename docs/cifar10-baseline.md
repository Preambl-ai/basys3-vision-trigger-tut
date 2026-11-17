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
