// Resource and timing model for a ResNet-8 dot-product datapath.
// A controller supplies one activation and a row of weights each cycle.
module resnet8_mac_array #(
    parameter integer LANES = 64,
    parameter integer WEIGHT_ROWS = 2048,
    parameter WEIGHT_FILE = "weights.mem"
) (
    input  logic clk,
    input  logic reset,
    input  logic valid,
    input  logic first_tap,
    input  logic [$clog2(WEIGHT_ROWS)-1:0] weight_address,
    input  logic [15:0] activation_address,
    input  logic signed [7:0] zero_point,
    input  logic activation_write,
    input  logic [15:0] activation_write_address,
    input  logic [7:0] activation_write_data,
    input  logic [$clog2(LANES)-1:0] result_lane,
    output logic signed [31:0] result
);
    localparam integer ACTIVATION_BYTES = 3 * 32 * 32 * 16;

    (* rom_style = "block" *) logic [8*LANES-1:0] weights [0:WEIGHT_ROWS-1];
    (* ram_style = "block" *) logic [7:0] activations [0:ACTIVATION_BYTES-1];
    initial $readmemh(WEIGHT_FILE, weights);

    logic [8*LANES-1:0] weight_read, weight_tap;
    logic signed [7:0] activation_read, zero_point_read;
    logic signed [8:0] activation_tap;
    logic read_valid, tap_valid, product_valid;
    logic read_first, tap_first, product_first;

    always_ff @(posedge clk) begin
        weight_read <= weights[weight_address];
        activation_read <= activations[activation_address];
        if (activation_write)
            activations[activation_write_address] <= activation_write_data;

        zero_point_read <= zero_point;
        weight_tap <= weight_read;
        activation_tap <= $signed({activation_read[7], activation_read})
                        - $signed({zero_point_read[7], zero_point_read});
        read_valid <= valid && !reset;
        tap_valid <= read_valid && !reset;
        product_valid <= tap_valid && !reset;
        read_first <= first_tap;
        tap_first <= read_first;
        product_first <= tap_first;
    end

    logic signed [31:0] sums [0:LANES-1];
    for (genvar lane = 0; lane < LANES; lane = lane + 1) begin : mac
        (* use_dsp = "yes" *) logic signed [16:0] product;
        wire signed [7:0] coefficient = weight_tap[lane*8 +: 8];
        wire signed [31:0] extended_product = {{15{product[16]}}, product};

        always_ff @(posedge clk) begin
            product <= activation_tap * coefficient;
            if (product_valid && !reset) begin
                if (product_first)
                    sums[lane] <= extended_product;
                else
                    sums[lane] <= sums[lane] + extended_product;
            end
        end
    end

    always_ff @(posedge clk)
        result <= sums[result_lane];
endmodule
