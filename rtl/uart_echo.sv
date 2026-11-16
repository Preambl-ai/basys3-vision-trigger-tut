module uart_echo #(
    parameter int unsigned CLOCKS_PER_BIT = 868
) (
    input  logic clk,
    input  logic uart_rx,
    output wire uart_tx,
    output wire led
);
    wire [7:0] rx_data;
    wire rx_valid;

    led_blink blinker (.clk(clk), .led(led));
    uart_rx_byte #(.CLOCKS_PER_BIT(CLOCKS_PER_BIT)) receiver (
        .clk(clk), .rx(uart_rx), .data(rx_data), .valid(rx_valid)
    );
    // The host waits for each echo before sending another byte.
    uart_tx_byte #(.CLOCKS_PER_BIT(CLOCKS_PER_BIT)) transmitter (
        .clk(clk), .data(rx_data), .valid(rx_valid), .ready(), .tx(uart_tx)
    );
endmodule
