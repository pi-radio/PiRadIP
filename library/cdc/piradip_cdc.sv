`timescale 1ns / 1ps

module piradip_cdc_auto_word #(
    parameter integer WIDTH = 32,
    parameter integer STAGES = 4,
    parameter RESET_VAL = 0
) (
    input logic              src_rst,
    input logic              src_clk,
    input logic  [WIDTH-1:0] src_data,
    input logic              src_send,

    input logic              dst_rst,
    input logic              dst_clk,
    output logic [WIDTH-1:0] dst_data,
    output logic             dst_update
);
  logic [WIDTH-1:0] dst_data_cdc;
  logic [WIDTH-1:0] src_data_r;
  logic [WIDTH-1:0] next_data_r;
  
  logic src_rcv, dst_req;
  logic dirty;
  logic sending;
   
	    
  always @(posedge src_clk) begin
    if (src_rst) begin
      dirty 	  <= 1'b0;
      sending 	  <= 1'b0;
      next_data_r <= 1'b0;
      src_data_r  <= 1'b0;
    end else if (src_rcv || sending) begin
      sending <= ~src_rcv;
      if (src_send) begin
	dirty <= 1'b1;
	next_data_r <= src_data;
      end
    end else begin
      src_data_r <= src_send ? src_data : next_data_r;
      sending 	 <= src_send | dirty;
      dirty 	 <= 1'b0;
    end
  end
  
  always @(posedge dst_clk) begin
    if (dst_req) begin
      dst_data <= dst_data_cdc;
      dst_update <= 1'b1;
    end else begin
      dst_update <= 1'b0;
    end
  end

  xpm_cdc_handshake #(
      .DEST_EXT_HSK(0),
      .DEST_SYNC_FF(STAGES),
      .INIT_SYNC_FF(0),
      .SIM_ASSERT_CHK(1),
      .WIDTH(WIDTH)
  ) cdc (
      .dest_clk(dst_clk),
      .dest_out(dst_data_cdc),
      .dest_req(dst_req),

      .src_rcv (src_rcv),
      .src_clk (src_clk),
      .src_in  (src_data_r),
      .src_send(sending)
  );
endmodule

module piradip_cdc_auto_reg #(
    parameter integer WIDTH  = 32,
    parameter integer STAGES = 4
) (
    input             src_rst,
    input             src_clk,
    input [WIDTH-1:0] src_data,

    input              dst_rst,
    input              dst_clk,
    output [WIDTH-1:0] dst_data,
    output             dst_update
);
  logic src_send;
  logic last_rst;
  logic [WIDTH-1:0] last_data;

  assign src_send = (last_rst != src_rst) || (last_data != src_data);

  always @(posedge src_clk) begin
    last_rst  <= src_rst;
    last_data <= src_data;
  end

  piradip_cdc_auto_word #(
      .WIDTH (WIDTH),
      .STAGES(STAGES)
  ) cdc (
      .*
  );
endmodule
