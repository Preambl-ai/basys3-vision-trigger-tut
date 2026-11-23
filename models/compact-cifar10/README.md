# Compact CIFAR-10 candidate

This directory contains the trained checkpoint and CPU exports for the first compact-model experiment. It predicts the ten CIFAR-10 classes from 32 × 32 RGB inputs.

- `checkpoint.pt`: float training weights, selected by validation accuracy.
- `float32.ts`: saved TorchScript model with batch normalization folded into convolutions.
- `int8.ts`: static INT8 TorchScript model, using PyTorch's oneDNN backend.
- `manifest.json`: SHA-256 hashes for these artifacts and the verified dataset source.

The exports take NCHW float32 inputs divided by 255 and return ten float32 logits. The INT8 export quantizes inputs internally. It uses signed 8-bit kernels and unsigned 8-bit activations. These files are CPU artifacts, not FPGA bitstreams.

The candidate's measured accuracy and limitations are recorded in the [experiment report](../../docs/compact-cifar10.md). The [raw evidence](../../docs/benchmarks/compact-cifar10/) includes the training settings, split indices, history, and full-test predictions. This is a single-seed, limited-budget experiment.

## Reproduce an evaluation without retraining

After following the experiment's environment setup, run from the repository root:

```powershell
& $compactPython ml/benchmark_compact.py models/compact-cifar10/checkpoint.pt --output runs/compact-cifar10/replay-float32
& $compactPython ml/benchmark_compact.py models/compact-cifar10/checkpoint.pt --int8 --output runs/compact-cifar10/replay-int8
```

These commands rebuild the exports from the same frozen checkpoint, verify export round trips, and evaluate the official test split. They need the verified CIFAR-10 archive; it downloads automatically if absent. Choose fresh output directories for repeat runs. Timing will vary by machine and workload.
