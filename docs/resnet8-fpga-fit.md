# ResNet-8 fit on the Basys 3

I checked how much FPGA hardware the INT8 ResNet-8 would need before building the full classifier. I used the same [published INT8 model](cifar10-baseline.md#int8-comparison) as the laptop benchmark and targeted the Basys 3's Artix-7 XC7A35T at 100 MHz in Vivado 2025.2.

## What I built

- I packed all 77,360 bytes of convolution and dense weights from the reference model into on-chip ROM. I allocated 48 KiB of activation RAM for an input, an output, and a residual buffer.
- I built 32- and 64-lane versions of the same dot-product circuit. Each cycle the circuit reads one activation and a row of weights, then multiplies and accumulates one product per lane.
- Both versions passed RTL simulation. I checked every lane's signed sum for one weight group from the first convolution and one from the last convolution, including a gap in the input stream.

The Vivado build covers the MAC array and its memories. Layer scheduling, bias, rescaling, residual adds, pooling, softmax, and board I/O still need an integrated build. The simulation checks dot products. The full-model score comparison uses the [saved laptop reference vectors](cifar10-baseline.md#reference-vectors-for-the-fpga) once the classifier is implemented.

## Vivado results

Both versions placed and routed. The constrained internal paths met the 10 ns clock period with positive worst setup slack. These out-of-context reports cover the datapath's internal timing. Board-level clock routing and I/O timing are part of a later integrated build.

| MAC lanes | Logic LUTs | DSPs | Block RAM tiles | Worst setup slack |
| ---: | ---: | ---: | ---: | ---: |
| 32 | 307 / 20,800 | 32 / 90 | 44.5 / 50 | +1.152 ns |
| 64 | 563 / 20,800 | 64 / 90 | 44.5 / 50 | +0.726 ns |

The datapath and its memories already use **89% of the available block RAM** in both builds.

## How fast would this design be?

ResNet-8 has **12.50 million dense multiply-accumulates per image** on the exported convolution and dense layers, counting padding taps. The 32-lane schedule needs **552,000 issue cycles** at one weight row per cycle, or **5.52 ms** at 100 MHz. The 64-lane schedule needs **494,656 cycles**, or **4.95 ms**. Both figures assume continuous issues and cover only the dot products.

The optimized laptop INT8 baseline was **about 0.22 ms** per image. Even an ideal 100 MHz design using all 90 Basys 3 DSPs at one MAC per DSP per cycle would need about **1.39 ms** to execute the dense count. For the speed demo, I would keep ResNet-8 as the accuracy baseline and test a smaller CIFAR-10 model with a much lower operation count, then remeasure accuracy and fit. [Digilent Basys 3 reference manual](https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf)

## Reproduce the build

Set up the [benchmark Python environment](cifar10-baseline.md#set-up-the-model-and-test-data). From the project root in PowerShell, use either 32 or 64 for `$lanes`. Set `$vivado` to your installation's executable.

```powershell
$lanes = 64
$vivado = 'C:/AMDDesignTools/2025.2/Vivado/bin/vivado.bat'
.\runs\cifar10-baseline\venv\Scripts\python.exe ml/export_resnet8_fit.py --lanes $lanes
& $vivado -mode batch -source scripts/build_resnet8_fit.tcl -tclargs $lanes
```

The build writes the model's operation counts in `model.json` and the Vivado results in `utilization-routed.rpt` and `timing.rpt` under `build/resnet8-fit/<lanes>/`.

To also replay the [dot-product simulation](../sim/resnet8_mac_array_tb.sv), run the following after exporting the weight rows. This uses Icarus Verilog.

```powershell
$build = "build/resnet8-fit/$lanes"
$rows = (Get-Content "$build/model.json" -Raw | ConvertFrom-Json).weight_rows
iverilog -g2012 -s resnet8_mac_array_tb -P "resnet8_mac_array_tb.LANES=$lanes" -P "resnet8_mac_array_tb.WEIGHT_ROWS=$rows" -o "$build/mac-test.vvp" rtl/resnet8_mac_array.sv sim/resnet8_mac_array_tb.sv
Push-Location $build
try { vvp mac-test.vvp } finally { Pop-Location }
```
