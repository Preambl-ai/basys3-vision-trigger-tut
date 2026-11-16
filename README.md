# Basys 3 Vision Trigger

Train a small vision classifier on a laptop, run it on a Digilent Basys 3 FPGA, and generate a hardware pulse when a selected event appears in a camera image.

## First demo

A fixed camera watches an object pass through a guide. The classifier checks a grayscale crop for an object that is visibly out of position. The Basys 3 will indicate a detection on an LED and pulse an output that can mark a recording.

The first demo will use a laptop to crop and send images over USB serial. The FPGA will run the trained CNN using weights stored in on-chip memory.

## Getting started

1. Install Git, VS Code, and AMD Vivado with Artix-7 support.
2. Connect the Basys 3 to your computer over its programming USB port.
3. Use the board manual and pin constraints below to build and program a simple LED blinker. Record the Vivado version and the steps that worked here.
4. Use a webcam or phone to record normal passes, out-of-position passes, and distracting motion. Check that the event remains visible in a 32 × 32 grayscale crop.

## Milestones

- [ ] Program and verify the LED blinker.
- [ ] Train a two-layer CNN in PyTorch and compare it with a simple image rule on clips from a different recording session.
- [ ] Export 8-bit weights and record expected scores for a small set of test images.
- [ ] Match the integer reference scores in simulation and on the Basys 3.
- [ ] Run the live camera demo and record missed events and false triggers.
- [ ] Compare on-chip weight storage with a build that uses the same weights as fixed coefficients.

## Benchmark notes

Record the source commit, model version, Vivado version, clock frequency, and input size for each run. Report FPGA processing time from the last accepted pixel to the decision separately from USB transfer and camera-to-output time. Include routed resource use when comparing builds.

## References

- [Digilent Basys 3 reference manual](https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf)
- [Digilent Basys 3 pin constraints](https://github.com/Digilent/digilent-xdc/blob/master/Basys-3-Master.xdc)
- [PyTorch model-building guide](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html)
