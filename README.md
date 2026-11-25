# Basys 3 Vision Trigger

A Preambl prototype for running a small camera classifier on a Basys 3 FPGA. The first demo detects when an eraser crosses a marked lane.

## CIFAR-10 benchmark

On 10,000 test images, ResNet-8 reached **87.19% at about 0.48 ms per image** in float32 and **86.97% at about 0.18 ms per image** with optimized INT8 CPU inference in the latest run. These are median laptop timings. [Results and reproduction steps](docs/cifar10-baseline.md)

The new compact CNN scored **75.74% in float32 and 75.48% in INT8** after 20 training epochs. It uses fewer weights and operations, but misses our **85% accuracy target** and was slower than optimized INT8 ResNet-8 in these CPU runs. [Experiment and saved models](docs/compact-cifar10.md) · [Measured comparison](docs/benchmarks/comparison.md)

## Camera test

The two-layer CNN trained on **9 grayscale images** and correctly classified **9 out of 9 images from a separate recording** on the laptop. Each input is 32 × 32 pixels. This first test used one eraser and one tabletop setup.

![Nine labeled test images showing the eraser inside the lane and crossing either line](docs/eraser-pilot/test-preview.png)

[Full test write-up](docs/eraser-pilot.md) · [Training video](docs/eraser-pilot/train-excerpts.mp4) · [Test video](docs/eraser-pilot/test-excerpts.mp4) · [Terminal output](docs/eraser-pilot/training-output.txt)

## Run the test

In PowerShell, run these from the project folder. Extract the [labeled images](docs/eraser-pilot/labeled-crops.zip) on your first run.

```powershell
python -m pip install -r ml/requirements.txt -r ml/requirements-model.txt
Expand-Archive docs/eraser-pilot/labeled-crops.zip -DestinationPath data/processed/eraser-pilot
python ml/train.py
```

## FPGA progress

- **On the board:** Verified the LED blink and USB serial echo, then sent a 32 × 32 test image and received all 1,024 pixels back.
- **Vivado:** ResNet-8's dot-product circuit and memories routed at 100 MHz. The 64-lane design used 89% of block RAM and would need about 4.95 ms per image for dot products alone. [Fit and timing results](docs/resnet8-fpga-fit.md)
- **Next:** Improve compact-model accuracy or test structural pruning, using validation data, before choosing a model for full FPGA implementation.

## Research: smaller models and faster hardware

We reviewed Qismet and research on pruning, quantization, and FPGA inference. **Compression is worth testing, but its benefit must be measured on the hardware.** Qismet's published results do not establish a quantum advantage.

The recommended experiment compares a directly trained smaller CNN with a structurally pruned model, using INT8 ResNet-8 as the reference. The first compact-model baseline is now measured; pruning and distillation have not been run. [Read the findings, sources, and proposed experiment](docs/research/model-compression.md).

We also reviewed **RRAM and compute-in-memory** as a possible future research track. An RRAM computing array could work alongside an FPGA, but the Basys 3 cannot implement physical RRAM through a bitstream. [Read the RRAM findings, hardware options, and proposed evaluation](docs/research/rram-compute-in-memory.md). No RRAM simulation or hardware experiment has been run in this project.

Our **ROMA review** examines fixed model weights with small, updateable adapters, related vision designs, and possible instrument applications. The proposed next experiment is a small fixed feature extractor with a writable classifier. ROMA's headline results are ASIC design projections, and this architecture has existing prior art. [Read the evidence, limitations, and proposed experiment](docs/research/roma-fixed-model-adapters.md). No adapter experiment has been run in this project.

[Basys 3 setup and hardware tests](docs/basys3-setup.md) · [Camera capture guide](docs/capture-clips.md)
