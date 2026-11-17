# Basys 3 setup and tests

The first milestone uses the board's 100 MHz clock to toggle LD0 every half-second. One full blink takes one second.

## Build the LED blinker

Install AMD Vivado with Artix-7 device support. From the repository root, run this in PowerShell with Vivado on your PATH.

```powershell
vivado -mode batch -source scripts/build_blink.tcl
```

If Vivado is installed outside your PATH, use the full path to `vivado.bat`. For example, on this computer the command is:

```powershell
& 'C:/AMDDesignTools/2025.2/Vivado/bin/vivado.bat' -mode batch -source scripts/build_blink.tcl
```

The build writes the bitstream to `build/blink/led_blink.bit` and saves timing and resource reports alongside it.

## Program the board

1. Connect the Basys 3 using a data-capable micro-USB cable at its programming port and turn the board on.
2. In Vivado, open **Hardware Manager**, then select **Open Target** and **Auto Connect**.
3. Select the Artix-7 device, choose **Program Device**, and select `build/blink/led_blink.bit`.
4. Look for **LD0** to turn on and off at half-second intervals. Programming this way loads the FPGA until power is removed.

## Run the simulation

With Icarus Verilog installed, run the following from the repository root. The simulation uses a shorter interval and checks the initial LED state and the exact toggle cycles.

```powershell
New-Item -ItemType Directory -Force build | Out-Null
iverilog -g2012 -s led_blink_tb -o build/led_blink.vvp rtl/led_blink.sv sim/led_blink_tb.sv
vvp build/led_blink.vvp
```

## Test the USB serial connection

The serial test keeps LD0 blinking and echoes one byte back through the board's USB programming port. The connection uses 115200 baud, eight data bits, no parity, and one stop bit. Send one byte at a time and wait for its reply.

Build the test from the repository root with Vivado.

```powershell
vivado -mode batch -source scripts/build_uart_echo.tcl
```

On the Basys 3, use **Program Device** in Vivado Hardware Manager to load `build/uart_echo/uart_echo.bit`. Then run this from the project's PowerShell terminal, using the port listed under **Ports (COM & LPT)** in Windows Device Manager.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r scripts/requirements-uart.txt
.\.venv\Scripts\python.exe scripts/test_uart.py COM5
```

The test should print `PASS: sent A and received A on COM5.`. An LED blink by itself does not verify the serial exchange. If the script times out, check that the serial test bitstream is loaded and the port number is correct.

To check the echo logic in simulation with Icarus Verilog:

```powershell
New-Item -ItemType Directory -Force build | Out-Null
iverilog -g2012 -s uart_echo_tb -o build/uart_echo.vvp rtl/led_blink.sv rtl/uart_byte.sv rtl/uart_echo.sv sim/uart_echo_tb.sv
vvp build/uart_echo.vvp
```

## Send a full test image over USB

This test uses a generated 32 × 32 image. The FPGA stores its 1,024 grayscale pixels in block RAM, then sends all 1,024 bytes back in row order. The laptop checks the returned bytes.

1. Build the new design with `vivado -mode batch -source scripts/build_frame_echo.tcl` from the repository root.
2. In Vivado Hardware Manager, use **Program Device** to load `build/frame_echo/frame_echo.bit`.
3. Run the command below from the project terminal. It uses the same Python environment and serial port as the one-byte test.

```powershell
.\.venv\Scripts\python.exe scripts/test_frame.py COM5
```

The expected result is `PASS: all 1,024 pixels matched on COM5.`

The request starts with `0xA5` followed by exactly 1,024 pixel bytes. The board starts replying after the last pixel is stored. A 100 ms gap between received bytes discards an incomplete image, and the test waits for that interval before retrying. Send the next image after receiving the current reply.

To check the frame buffer in simulation with Icarus Verilog:

```powershell
New-Item -ItemType Directory -Force build | Out-Null
iverilog -g2012 -s frame_echo_tb -o build/frame_echo.vvp rtl/led_blink.sv rtl/uart_byte.sv rtl/frame_echo.sv sim/frame_echo_tb.sv
vvp build/frame_echo.vvp
```

## Benchmark notes

Record the source commit, model version, Vivado version, clock frequency, and input size for each run. Report FPGA processing time from the last accepted pixel to the decision separately from USB transfer and camera-to-output time. Include routed resource use when comparing builds.

## References

- [Digilent Basys 3 reference manual](https://digilent.com/reference/_media/reference/programmable-logic/basys-3/basys3_rm.pdf)
- [Digilent Basys 3 pin constraints](https://github.com/Digilent/digilent-xdc/blob/master/Basys-3-Master.xdc)
- [PyTorch model-building guide](https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html)
