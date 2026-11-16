# Basys 3 W5 clock and LD0 pin assignments from Digilent's master XDC.
set_property -dict {PACKAGE_PIN W5 IOSTANDARD LVCMOS33} [get_ports clk]
create_clock -name sys_clk -period 10.000 [get_ports clk]
set_property -dict {PACKAGE_PIN U16 IOSTANDARD LVCMOS33} [get_ports led]
