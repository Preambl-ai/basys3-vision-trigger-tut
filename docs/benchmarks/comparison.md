# CIFAR-10 model comparison

Measured CPU results: 10,000 official test images, batch one, one CPU thread.
Runtime, date, and machine differences can affect timings. These are not FPGA measurements.

The project requires at least 85% accuracy. A smaller or faster model below that threshold does not pass.

| Model | Runtime | Accuracy | Core median (ms) | Core p95 (ms) | Host median (ms) | Dense MACs | Kernel parameters | Kernel weight bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MLPerf Tiny ResNet-8 float32 | LiteRT 2.3.0 CPU | 87.19% | 0.4826 | 0.7928 | 0.4869 | 12501632 | 77360 | 309440 |
| MLPerf Tiny ResNet-8 int8 | LiteRT 2.3.0 CPU | 86.97% | 0.1780 | 0.3561 | 0.1812 | 12501632 | 77360 | 77360 |
| CompactCNN float32 | PyTorch 2.9.0+cpu TorchScript CPU | 75.74% | 0.5302 | 1.8541 | 0.5540 | 2580800 | 18392 | 73568 |
| CompactCNN int8 | PyTorch 2.9.0+cpu TorchScript CPU | 75.48% | 0.5531 | 2.8064 | 0.5912 | 2580800 | 18392 | 18392 |

MAC counts cover convolution and linear products, including padded taps;
they exclude pooling, activation, rescaling, and data movement.
Kernel bytes exclude biases, scales, metadata, and FPGA packing overhead.
Missing resource data is shown as unreported, never as zero.

## Source results

- `docs/benchmarks/resnet8-float32-current.json` — model SHA-256 `b5c0046d6e0328b4956afd6baa29555a29b1f1c65bdd45aaed75b7cd484d9f79`
- `docs/benchmarks/resnet8-int8-current.json` — model SHA-256 `3c002613d1b2475eb51dd78dfb85a546c8ae658dee71cf6ade43b022fe205415`
- `docs/benchmarks/compact-cifar10/float32.json` — model SHA-256 `365ff0d95f56788d75a07b8765a690b892114e6871e1b9c03adfca2f7ff8ac82`
- `docs/benchmarks/compact-cifar10/int8.json` — model SHA-256 `f6c2f1c1d81b31f5525cfd855b8bd2f5d4f73827e22b9933ffb45125cb3b931b`
