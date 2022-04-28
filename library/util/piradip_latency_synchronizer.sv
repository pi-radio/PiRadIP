`timescale 1ns / 1ps

module piradip_latency_synchronizer #(
    parameter integer OUT_OF_BAND_WIDTH = 1,
    parameter integer IN_BAND_WIDTH = 32,
    parameter integer DATA_LATENCY = 1
) (
    input clk,
    input resetn,
    input in_valid,
    input [IN_BAND_WIDTH-1:0] in_band,
    input [OUT_OF_BAND_WIDTH-1:0] out_of_band,
    output out_valid,
    output [IN_BAND_WIDTH+OUT_OF_BAND_WIDTH-1:0] out_data
);
  logic [OUT_OF_BAND_WIDTH:0] oob_out;

  assign {out_valid, out_data} = {oob_out, in_band};

  genvar i;

  generate
    logic [OUT_OF_BAND_WIDTH:0] oob_cat;

    if (OUT_OF_BAND_WIDTH > 0) begin
      assign oob_cat = {in_valid, out_of_band};
    end else begin
      assign oob_cat = in_valid;
    end

    if (DATA_LATENCY > 1) begin
      logic [OUT_OF_BAND_WIDTH:0] oob_fifo[0:DATA_LATENCY-1];

      for (i = 0; i < DATA_LATENCY - 1; i = i + 1) begin
        always @(posedge clk) oob_fifo[i] <= (resetn) ? oob_fifo[i+1] : 0;
      end

      always @(posedge clk) oob_fifo[i+1] <= (resetn) ? oob_cat : 0;

      assign oob_out = oob_fifo[0];
    end else begin
      always @(posedge clk) oob_out <= (resetn) ? oob_cat : 0;
    end
  endgenerate

endmodule
