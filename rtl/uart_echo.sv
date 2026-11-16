module uart_echo #(
    parameter int unsigned CLOCKS_PER_BIT = 868
) (
    input  logic clk,
    input  logic uart_rx,
    output wire uart_tx,
    output wire led
);
    localparam int COUNT_WIDTH = $clog2(CLOCKS_PER_BIT);
    localparam logic [COUNT_WIDTH-1:0] BIT_DELAY = COUNT_WIDTH'(CLOCKS_PER_BIT - 1);
    localparam logic [COUNT_WIDTH-1:0] START_DELAY = COUNT_WIDTH'(CLOCKS_PER_BIT / 2 - 1);

    typedef enum logic [1:0] {IDLE, START_BIT, DATA_BITS, STOP_BIT} rx_state_t;
    rx_state_t rx_state = IDLE;

    (* ASYNC_REG = "TRUE" *) logic [1:0] rx_sync = 2'b11;
    logic [COUNT_WIDTH-1:0] rx_count = '0;
    logic [2:0] rx_index = '0;
    logic [7:0] rx_data = '0;
    logic rx_valid = 1'b0;

    logic [COUNT_WIDTH-1:0] tx_count = '0;
    logic [3:0] tx_remaining = '0;
    logic [9:0] tx_shift = '1;

    led_blink blinker (.clk(clk), .led(led));
    assign uart_tx = tx_shift[0];

    always_ff @(posedge clk) begin
        rx_sync <= {rx_sync[0], uart_rx};
        rx_valid <= 1'b0;

        if (rx_state == IDLE) begin
            if (!rx_sync[1]) begin
                rx_state <= START_BIT;
                rx_count <= START_DELAY;
            end
        end else if (rx_count != 0) begin
            rx_count <= rx_count - 1'b1;
        end else begin
            // After checking the center of the start bit, sample once per bit.
            rx_count <= BIT_DELAY;
            case (rx_state)
                START_BIT: begin
                    if (rx_sync[1]) begin
                        rx_state <= IDLE;
                    end else begin
                        rx_index <= '0;
                        rx_state <= DATA_BITS;
                    end
                end
                DATA_BITS: begin
                    rx_data[rx_index] <= rx_sync[1];
                    rx_index <= rx_index + 1'b1;
                    if (rx_index == 3'd7)
                        rx_state <= STOP_BIT;
                end
                STOP_BIT: begin
                    rx_valid <= rx_sync[1];
                    rx_state <= IDLE;
                end
                default: rx_state <= IDLE;
            endcase
        end
    end

    // The host sends one byte, then waits for its echo before sending another.
    always_ff @(posedge clk) begin
        if (tx_remaining == 0) begin
            if (rx_valid) begin
                tx_shift <= {1'b1, rx_data, 1'b0};
                tx_remaining <= 4'd10;
                tx_count <= BIT_DELAY;
            end
        end else if (tx_count == 0) begin
            tx_shift <= {1'b1, tx_shift[9:1]};
            tx_remaining <= tx_remaining - 1'b1;
            tx_count <= BIT_DELAY;
        end else begin
            tx_count <= tx_count - 1'b1;
        end
    end
endmodule
