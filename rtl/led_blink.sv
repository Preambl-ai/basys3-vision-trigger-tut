module led_blink #(
    parameter int unsigned HALF_PERIOD_CYCLES = 50_000_000
) (
    input  logic clk,
    output logic led = 1'b0
);
    localparam int COUNTER_WIDTH = (HALF_PERIOD_CYCLES <= 1)
        ? 1 : $clog2(HALF_PERIOD_CYCLES);
    localparam logic [COUNTER_WIDTH-1:0] LAST_CYCLE =
        COUNTER_WIDTH'(HALF_PERIOD_CYCLES - 1);

    logic [COUNTER_WIDTH-1:0] counter = '0;

    always_ff @(posedge clk) begin
        if (counter == LAST_CYCLE) begin
            counter <= '0;
            led <= ~led;
        end else begin
            counter <= counter + 1'b1;
        end
    end
endmodule
