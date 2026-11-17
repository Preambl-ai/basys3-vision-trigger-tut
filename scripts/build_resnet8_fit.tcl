if {$argc != 1 || [lindex $argv 0] ni {32 64}} {
    error "Pass 32 or 64 MAC lanes with -tclargs."
}
set lanes [lindex $argv 0]
set repo_root [file dirname [file dirname [file normalize [info script]]]]
set output_dir [file join $repo_root build resnet8-fit $lanes]
set weight_file [file join $output_dir weights.mem]
if {![file isfile $weight_file]} {
    error "Run ml/export_resnet8_fit.py --lanes $lanes before Vivado."
}
set handle [open $weight_file r]
set rows [llength [split [string trim [read $handle]] "\n"]]
close $handle

# The memory initializer is relative to Vivado's working directory.
cd $output_dir
read_verilog -sv [file join $repo_root rtl resnet8_mac_array.sv]
set handle [open clock.xdc w]
puts $handle {create_clock -name sys_clk -period 10.000 [get_ports clk]}
close $handle
read_xdc clock.xdc
synth_design -top resnet8_mac_array -part xc7a35tcpg236-1 -mode out_of_context \
    -generic [list LANES=$lanes WEIGHT_ROWS=$rows]
opt_design
report_utilization -file [file join $output_dir utilization.rpt]
place_design
route_design
report_timing_summary -file [file join $output_dir timing.rpt]
report_utilization -file [file join $output_dir utilization-routed.rpt]
