set repo_root [file dirname [file dirname [file normalize [info script]]]]
set output_dir [file join $repo_root build frame_echo]
file mkdir $output_dir

read_verilog -sv [list [file join $repo_root rtl led_blink.sv] \
    [file join $repo_root rtl uart_byte.sv] [file join $repo_root rtl frame_echo.sv]]
read_xdc [file join $repo_root rtl basys3.xdc]
read_xdc [file join $repo_root rtl basys3_uart.xdc]
synth_design -top frame_echo -part xc7a35tcpg236-1
opt_design
place_design
route_design

report_timing_summary -file [file join $output_dir timing.rpt]
report_utilization -file [file join $output_dir utilization.rpt]
write_bitstream -force [file join $output_dir frame_echo.bit]
