`timescale 1ns/1ps

module frame_echo_tb;
    localparam int BIT_CYCLES = 16;
    localparam int TIMEOUT_CYCLES = 512;
    logic clk = 1'b0;
    logic [7:0] outgoing = '0;
    logic outgoing_valid = 1'b0;
    wire outgoing_ready;
    wire host_to_fpga;
    wire fpga_to_host;
    wire [7:0] incoming;
    wire incoming_valid;

    int frame_seed = 0;
    int received = 0;
    logic expect_frame = 1'b0;

    always #5 clk = ~clk;

    frame_echo #(.CLOCKS_PER_BIT(BIT_CYCLES), .INTER_BYTE_TIMEOUT(TIMEOUT_CYCLES)) dut (
        .clk(clk), .uart_rx(host_to_fpga), .uart_tx(fpga_to_host), .led()
    );
    uart_tx_byte #(.CLOCKS_PER_BIT(BIT_CYCLES)) host_tx (
        .clk(clk), .data(outgoing), .valid(outgoing_valid),
        .ready(outgoing_ready), .tx(host_to_fpga)
    );
    uart_rx_byte #(.CLOCKS_PER_BIT(BIT_CYCLES)) host_rx (
        .clk(clk), .rx(fpga_to_host), .data(incoming), .valid(incoming_valid)
    );

    function automatic logic [7:0] pixel(input int index, input int seed);
        if (index == 123)
            return 8'hA5; // The header value is also allowed inside the image.
        return 8'((index * 37) ^ (index >> 3) ^ seed);
    endfunction

    always @(posedge clk) begin
        if (incoming_valid) begin
            if (!expect_frame || received >= 1024)
                $fatal(1, "Unexpected reply from the FPGA");
            if (incoming !== pixel(received, frame_seed))
                $fatal(1, "Pixel %0d differed: got %h", received, incoming);
            received = received + 1;
        end
    end

    task automatic send_byte(input logic [7:0] value);
        @(negedge clk);
        while (!outgoing_ready) @(negedge clk);
        outgoing <= value;
        outgoing_valid <= 1'b1;
        @(negedge clk);
        outgoing_valid <= 1'b0;
    endtask

    task automatic round_trip(input int seed);
        received = 0;
        frame_seed = seed;
        send_byte(8'hA5);
        for (int index = 0; index < 1023; index++)
            send_byte(pixel(index, seed));
        // No transmission may start before the last pixel is sent.
        expect_frame = 1'b1;
        send_byte(pixel(1023, seed));
        wait (received == 1024);
        repeat (12 * BIT_CYCLES) @(negedge clk);
        expect_frame = 1'b0;
    endtask

    initial begin
        send_byte(8'hA5);
        send_byte(8'hFF);
        send_byte(8'hFF);
        repeat (TIMEOUT_CYCLES + 12 * BIT_CYCLES) @(negedge clk);
        send_byte(8'h5A); // A non-header byte after timeout must be ignored.
        round_trip(23);
        round_trip(95);
        $display("PASS: two complete 1,024-byte frames echoed after a truncated frame");
        $finish;
    end

    initial begin
        #10_000_000;
        $fatal(1, "Frame echo test timed out");
    end
endmodule
