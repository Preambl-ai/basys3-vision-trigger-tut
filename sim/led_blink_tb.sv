`timescale 1ns/1ps

module led_blink_tb;
    logic clk = 1'b0;
    logic led;

    led_blink #(.HALF_PERIOD_CYCLES(4)) dut (.clk(clk), .led(led));
    always #5 clk = ~clk;

    initial begin
        #1;
        if (led !== 1'b0)
            $fatal(1, "LED must start off");

        for (int cycle = 1; cycle <= 16; cycle++) begin
            @(negedge clk);
            if (led !== ((cycle / 4) % 2 == 1))
                $fatal(1, "Unexpected LED state after clock cycle %0d", cycle);
        end

        $display("PASS: LED starts off and toggles every four cycles");
        $finish;
    end
endmodule
