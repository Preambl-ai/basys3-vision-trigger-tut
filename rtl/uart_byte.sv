module uart_rx_byte #(
    parameter int unsigned CLOCKS_PER_BIT = 868
) (
    input  logic clk,
    input  logic rx,
    output logic [7:0] data = '0,
    output logic valid = 1'b0
);
    localparam int COUNT_WIDTH = $clog2(CLOCKS_PER_BIT);
    localparam logic [COUNT_WIDTH-1:0] BIT_DELAY = COUNT_WIDTH'(CLOCKS_PER_BIT - 1);
    localparam logic [COUNT_WIDTH-1:0] START_DELAY = COUNT_WIDTH'(CLOCKS_PER_BIT / 2 - 1);

    typedef enum logic [1:0] {IDLE, START_BIT, DATA_BITS, STOP_BIT} state_t;
    state_t state = IDLE;

    (* ASYNC_REG = "TRUE" *) logic [1:0] rx_sync = 2'b11;
    logic [COUNT_WIDTH-1:0] count = '0;
    logic [2:0] index = '0;

    always_ff @(posedge clk) begin
        rx_sync <= {rx_sync[0], rx};
        valid <= 1'b0;

        if (state == IDLE) begin
            if (!rx_sync[1]) begin
                state <= START_BIT;
                count <= START_DELAY;
            end
        end else if (count != 0) begin
            count <= count - 1'b1;
        end else begin
            // After checking the center of the start bit, sample once per bit.
            count <= BIT_DELAY;
            case (state)
                START_BIT: begin
                    if (rx_sync[1]) begin
                        state <= IDLE;
                    end else begin
                        index <= '0;
                        state <= DATA_BITS;
                    end
                end
                DATA_BITS: begin
                    data[index] <= rx_sync[1];
                    index <= index + 1'b1;
                    if (index == 3'd7)
                        state <= STOP_BIT;
                end
                STOP_BIT: begin
                    valid <= rx_sync[1];
                    state <= IDLE;
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule

module uart_tx_byte #(
    parameter int unsigned CLOCKS_PER_BIT = 868
) (
    input  logic clk,
    input  logic [7:0] data,
    input  logic valid,
    output wire ready,
    output wire tx
);
    localparam int COUNT_WIDTH = $clog2(CLOCKS_PER_BIT);
    localparam logic [COUNT_WIDTH-1:0] BIT_DELAY = COUNT_WIDTH'(CLOCKS_PER_BIT - 1);

    logic [COUNT_WIDTH-1:0] count = '0;
    logic [3:0] remaining = '0;
    logic [9:0] shift = '1;

    assign ready = remaining == 0;
    assign tx = shift[0];

    always_ff @(posedge clk) begin
        if (ready) begin
            if (valid) begin
                shift <= {1'b1, data, 1'b0};
                remaining <= 4'd10;
                count <= BIT_DELAY;
            end
        end else if (count == 0) begin
            shift <= {1'b1, shift[9:1]};
            remaining <= remaining - 1'b1;
            count <= BIT_DELAY;
        end else begin
            count <= count - 1'b1;
        end
    end
endmodule
