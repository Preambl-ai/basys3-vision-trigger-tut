# Basys 3 Vision Trigger

Train a small vision classifier on a laptop, run it on a Digilent Basys 3 FPGA, and generate a hardware pulse when a selected event appears in a camera image.

## First demo

A fixed camera watches an object pass through a guide. The classifier checks a grayscale crop for an object that is visibly out of position. The Basys 3 will indicate a detection on an LED and pulse an output that can mark a recording.

The first demo will use a laptop to crop and send images over USB serial. The FPGA will run the trained CNN using weights stored in on-chip memory.

## Getting started

The first milestone uses the board's 100 MHz clock to toggle LD0 every half-second. One full blink takes one second.

### Build the LED blinker

Install AMD Vivado with Artix-7 device support. From the repository root, run this in PowerShell with Vivado on your PATH.

```powershell
vivado -mode batch -source scripts/build_blink.tcl
```

If Vivado is installed outside your PATH, use the full path to `vivado.bat`. For example, on this computer the command is:

```powershell
& 'C:/AMDDesignTools/2025.2/Vivado/bin/vivado.bat' -mode batch -source scripts/build_blink.tcl
```

The build writes the bitstream to `build/blink/led_blink.bit` and saves timing and resource reports alongside it.

### Program the board

1. Connect the Basys 3 using a data-capable micro-USB cable at its programming port and turn the board on.
2. In Vivado, open **Hardware Manager**, then select **Open Target** and **Auto Connect**.
3. Select the Artix-7 device, choose **Program Device**, and select `build/blink/led_blink.bit`.
4. Look for **LD0** to turn on and off at half-second intervals. Programming this way loads the FPGA until power is removed.

### Run the simulation

With Icarus Verilog installed, run the following from the repository root. The simulation uses a shorter interval and checks the initial LED state and the exact toggle cycles.

```powershell
New-Item -ItemType Directory -Force build | Out-Null
iverilog -g2012 -s led_blink_tb -o build/led_blink.vvp rtl/led_blink.sv sim/led_blink_tb.sv
vvp build/led_blink.vvp
```

## Prepare the CNN inputs

Use the [clip capture and crop preview guide](docs/capture-clips.md) to check the first camera recordings on your laptop.

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
