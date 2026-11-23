# Basys 3 Vision Trigger

A Preambl prototype for running a small camera classifier on a Basys 3 FPGA. The first demo detects when an eraser crosses a marked lane.

## CIFAR-10 benchmark

On 10,000 test images, ResNet-8 reached **87.19% at about 0.65 ms per image** in float32 and **86.97% at about 0.22 ms per image** with optimized INT8 CPU inference. These are median laptop timings. [Results and reproduction steps](docs/cifar10-baseline.md)

The compact-model experiment adds a smaller CNN, a fixed training/validation split, INT8 export, and full-test CPU benchmarking. [Run the experiment](docs/compact-cifar10.md) · [Measured model comparison](docs/benchmarks/comparison.md)

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
- **Next:** Benchmark a smaller CIFAR-10 model that can meet the speed target on the Basys 3.

## Research: smaller models and faster hardware

We reviewed Qismet and research on pruning, quantization, and FPGA inference. **Compression is worth testing, but its benefit must be measured on the hardware.** Qismet's published results do not establish a quantum advantage.

The recommended experiment compares a directly trained smaller CNN with a structurally pruned model, using the existing INT8 ResNet-8 as the reference. [Read the findings, sources, and proposed experiment](docs/research/model-compression.md). This is a research recommendation; these experiments have not been run yet.

We also reviewed **RRAM and compute-in-memory** as a possible future research track. An RRAM computing array could work alongside an FPGA, but the Basys 3 cannot implement physical RRAM through a bitstream. [Read the RRAM findings, hardware options, and proposed evaluation](docs/research/rram-compute-in-memory.md). No RRAM simulation or hardware experiment has been run in this project.

[Basys 3 setup and hardware tests](docs/basys3-setup.md) · [Camera capture guide](docs/capture-clips.md)
