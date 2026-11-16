set repo_root [file dirname [file dirname [file normalize [info script]]]]
set output_dir [file join $repo_root build blink]
file mkdir $output_dir

read_verilog -sv [file join $repo_root rtl led_blink.sv]
read_xdc [file join $repo_root rtl basys3.xdc]
synth_design -top led_blink -part xc7a35tcpg236-1
opt_design
place_design
route_design

report_timing_summary -file [file join $output_dir timing.rpt]
report_utilization -file [file join $output_dir utilization.rpt]
write_bitstream -force [file join $output_dir led_blink.bit]
