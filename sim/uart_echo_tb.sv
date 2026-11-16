`timescale 1ns/1ps

module uart_echo_tb;
    localparam int BIT_CYCLES = 868;
    logic clk = 1'b0;
    logic uart_rx = 1'b1;
    wire uart_tx;
    logic expect_echo = 1'b0;

    uart_echo #(.CLOCKS_PER_BIT(BIT_CYCLES)) dut (
        .clk(clk), .uart_rx(uart_rx), .uart_tx(uart_tx), .led()
    );

    always #5 clk = ~clk;

    always @(negedge uart_tx)
        if (!expect_echo)
            $fatal(1, "Unexpected serial transmission");

    task automatic drive_bit(input logic bit_value);
        uart_rx = bit_value;
        repeat (BIT_CYCLES) @(negedge clk);
    endtask

    task automatic send_byte(input logic [7:0] value, input logic valid_stop);
        @(negedge clk);
        drive_bit(1'b0);
        for (int i = 0; i < 8; i++)
            drive_bit(value[i]);
        drive_bit(valid_stop);
        uart_rx = 1'b1;
    endtask

    task automatic check_echo(input logic [7:0] expected);
        @(negedge uart_tx);
        repeat (BIT_CYCLES / 2) @(negedge clk);
        if (uart_tx !== 1'b0)
            $fatal(1, "Missing start bit");
        for (int i = 0; i < 8; i++) begin
            repeat (BIT_CYCLES) @(negedge clk);
            if (uart_tx !== expected[i])
                $fatal(1, "Wrong data bit %0d in echo for %h", i, expected);
        end
        repeat (BIT_CYCLES) @(negedge clk);
        if (uart_tx !== 1'b1)
            $fatal(1, "Missing stop bit");
    endtask

    task automatic round_trip(input logic [7:0] value);
        expect_echo = 1'b1;
        fork
            send_byte(value, 1'b1);
            check_echo(value);
        join
        repeat (BIT_CYCLES) @(negedge clk);
        expect_echo = 1'b0;
    endtask

    initial begin
        repeat (BIT_CYCLES) @(negedge clk);
        if (uart_tx !== 1'b1)
            $fatal(1, "Serial output must be high while idle");

        send_byte(8'h41, 1'b0);
        repeat (12 * BIT_CYCLES) @(negedge clk);

        round_trip(8'h41);
        round_trip(8'h96);
        round_trip(8'h00);
        round_trip(8'hFF);
        $display("PASS: four bytes echoed and invalid stop bit ignored");
        $finish;
    end

    initial begin
        #(1_500 * BIT_CYCLES);
        $fatal(1, "Serial test timed out");
    end
endmodule
