# CIFAR-10 model comparison

Measured CPU results: 10,000 official test images, batch one, one CPU thread.
Runtime, date, and machine differences can affect timings. These are not FPGA measurements.

| Model | Runtime | Accuracy | Core median (ms) | Core p95 (ms) | Host median (ms) | Dense MACs | Kernel parameters | Kernel weight bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MLPerf Tiny ResNet-8 float32 | LiteRT 2.3.0 | 87.19% | 0.6544 | 1.0759 | 0.6626 | 12501632 | 77360 | 309440 |
| MLPerf Tiny ResNet-8 int8 | LiteRT 2.3.0 | 86.97% | 0.2159 | 0.2966 | 0.2193 | 12501632 | 77360 | 77360 |

MAC counts cover convolution and linear products, including padded taps;
they exclude pooling, activation, rescaling, and data movement.
Kernel bytes exclude biases, scales, metadata, and FPGA packing overhead.
Missing resource data is shown as unreported, never as zero.

## Source results

- `docs/benchmarks/resnet8-float32.json` — model SHA-256 `b5c0046d6e0328b4956afd6baa29555a29b1f1c65bdd45aaed75b7cd484d9f79`
- `docs/benchmarks/resnet8-int8.json` — model SHA-256 `3c002613d1b2475eb51dd78dfb85a546c8ae658dee71cf6ade43b022fe205415`
