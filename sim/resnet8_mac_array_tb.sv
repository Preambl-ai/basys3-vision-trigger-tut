`timescale 1ns/1ps
module resnet8_mac_array_tb #(
    parameter integer LANES = 64,
    parameter integer WEIGHT_ROWS = 2048
);
    logic clk = 0;
    always #5 clk = ~clk;

    logic reset = 1, valid = 0, first_tap = 0, activation_write = 0;
    logic [$clog2(WEIGHT_ROWS)-1:0] weight_address = 0;
    logic [15:0] activation_address = 0, activation_write_address = 0;
    logic signed [7:0] zero_point = 0;
    logic [7:0] activation_write_data = 0;
    logic [$clog2(LANES)-1:0] result_lane = 0;
    logic signed [31:0] result;
    logic [7:0] test_inputs [0:602];
    logic signed [31:0] expected [0:2*LANES-1];

    resnet8_mac_array #(.LANES(LANES), .WEIGHT_ROWS(WEIGHT_ROWS)) dut (.*);

    integer cases, start_row, taps, input_zero, input_offset;
    initial begin
        $readmemh("dot_inputs.mem", test_inputs);
        $readmemh("dot_expected.mem", expected);
        cases = $fopen("dot_cases.txt", "r");
        if (!cases) $fatal(1, "Cannot open dot_cases.txt");
        input_offset = 0;

        repeat (2) @(negedge clk);
        reset = 0;
        for (integer trial = 0; trial < 2; trial = trial + 1) begin
            if ($fscanf(cases, "%d %d %d", start_row, taps, input_zero) != 3)
                $fatal(1, "Invalid dot-product case %0d", trial);
            for (integer tap = 0; tap < taps; tap = tap + 1) begin
                @(negedge clk);
                activation_write = 1;
                activation_write_address = tap;
                activation_write_data = test_inputs[input_offset + tap];
            end
            @(negedge clk);
            activation_write = 0;
            zero_point = input_zero;
            for (integer tap = 0; tap < taps; tap = tap + 1) begin
                if (tap == 13) begin
                    valid = 0;
                    @(negedge clk);
                end
                valid = 1;
                first_tap = (tap == 0);
                activation_address = tap;
                weight_address = start_row + tap;
                @(negedge clk);
            end
            valid = 0;
            repeat (5) @(negedge clk);
            for (integer lane = 0; lane < LANES; lane = lane + 1) begin
                result_lane = lane;
                @(posedge clk);
                #1;
                if (result !== expected[trial*LANES + lane])
                    $fatal(1, "Case %0d lane %0d: got %0d, expected %0d",
                           trial, lane, result, expected[trial*LANES + lane]);
                @(negedge clk);
            end
            input_offset = input_offset + taps;
        end
        $fclose(cases);
        $display("PASS: %0d lanes matched both ResNet-8 weight groups.", LANES);
        $finish;
    end
endmodule
