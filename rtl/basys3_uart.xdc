# UART pin assignments from Digilent's Basys 3 master XDC.
set_property -dict {PACKAGE_PIN B18 IOSTANDARD LVCMOS33} [get_ports uart_rx]
set_property -dict {PACKAGE_PIN A18 IOSTANDARD LVCMOS33} [get_ports uart_tx]
