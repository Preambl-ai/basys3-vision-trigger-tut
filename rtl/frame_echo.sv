module frame_echo #(
    parameter int unsigned CLOCKS_PER_BIT = 868,
    parameter int unsigned INTER_BYTE_TIMEOUT = 10_000_000
) (
    input  logic clk,
    input  logic uart_rx,
    output wire uart_tx,
    output wire led
);
    localparam logic [7:0] HEADER = 8'hA5;
    localparam int ADDRESS_WIDTH = 10;
    localparam int TIMEOUT_WIDTH = $clog2(INTER_BYTE_TIMEOUT);
    localparam logic [TIMEOUT_WIDTH-1:0] LAST_TICK = TIMEOUT_WIDTH'(INTER_BYTE_TIMEOUT - 1);

    typedef enum logic [1:0] {WAIT_HEADER, RECEIVE, READ_PIXEL, SEND_PIXEL} state_t;
    state_t state = WAIT_HEADER;
    logic [ADDRESS_WIDTH-1:0] address = '0;
    logic [TIMEOUT_WIDTH-1:0] gap_count = '0;

    (* ram_style = "block" *) logic [7:0] pixels [0:(1 << ADDRESS_WIDTH)-1];
    logic [7:0] buffered_pixel;
    wire [7:0] rx_data;
    wire rx_valid;
    wire tx_ready;
    wire tx_valid = state == SEND_PIXEL;

    led_blink blinker (.clk(clk), .led(led));
    uart_rx_byte #(.CLOCKS_PER_BIT(CLOCKS_PER_BIT)) receiver (
        .clk(clk), .rx(uart_rx), .data(rx_data), .valid(rx_valid)
    );
    uart_tx_byte #(.CLOCKS_PER_BIT(CLOCKS_PER_BIT)) transmitter (
        .clk(clk), .data(buffered_pixel), .valid(tx_valid), .ready(tx_ready), .tx(uart_tx)
    );

    // Use the same memory port for receiving and replaying the image.
    always_ff @(posedge clk) begin
        if (state == RECEIVE && rx_valid)
            pixels[address] <= rx_data;
        else if (state == READ_PIXEL)
            buffered_pixel <= pixels[address];
    end

    always_ff @(posedge clk) begin
        case (state)
            WAIT_HEADER: begin
                if (rx_valid && rx_data == HEADER) begin
                    address <= '0;
                    gap_count <= '0;
                    state <= RECEIVE;
                end
            end
            RECEIVE: begin
                if (rx_valid) begin
                    gap_count <= '0;
                    address <= address + 1'b1;
                    // The address wraps to zero for readback after the final write.
                    if (&address)
                        state <= READ_PIXEL;
                end else if (gap_count == LAST_TICK) begin
                    // Stop waiting for a truncated image and accept a new header.
                    state <= WAIT_HEADER;
                end else begin
                    gap_count <= gap_count + 1'b1;
                end
            end
            READ_PIXEL: state <= SEND_PIXEL;
            SEND_PIXEL: begin
                if (tx_ready) begin
                    address <= address + 1'b1;
                    if (&address)
                        state <= WAIT_HEADER;
                    else
                        state <= READ_PIXEL;
                end
            end
        endcase
    end
endmodule
