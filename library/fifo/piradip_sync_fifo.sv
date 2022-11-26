`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 03/30/2022 05:27:57 PM
// Design Name:
// Module Name: piradip_sync_fifo
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

`define DIGIT_CONDITIONAL(x, y) (x == y) ? $toupper(`"y`")
`define HEX_CHAR(x) ( \
    (x == 0) ? "0"  : (x == 1) ? "1"  : (x == 2) ? "2"  : (x == 3) ? "3" : \
    (x == 4) ? "4"  : (x == 5) ? "5"  : (x == 6) ? "6"  : (x == 7) ? "7" : \
    (x == 8) ? "8"  : (x == 9) ? "9"  : (x == 10) ? "A" : (x == 11) ? "B" : \
    (x == 12) ? "C" : (x == 13) ? "D" : (x == 14) ? "E" : (x == 15) ? "F" : \
    "?" )

`define TEST_BO(x) ((x) ? 1'b1 : 1'b0)

module piradip_sync_fifo #(
    parameter WIDTH = 32,
    parameter DEPTH = 16,
    parameter READ_LATENCY = 1,
    parameter PROG_FULL_THRESH = 0,
    parameter PROG_EMPTY_THRESH = 0,
    parameter OVERFLOW = 1,
    parameter UNDERFLOW = 1,
    parameter WRITE_DATA_COUNT_WIDTH = 0,
    parameter READ_DATA_COUNT_WIDTH = 0,
    parameter ALMOST_FULL = 0,
    parameter ALMOST_EMPTY = 0,
    parameter DATA_VALID = 0,
    parameter WRITE_ACK = 0
) (
    input clk,
    input rst,
    input sleep,

    input we,
    input [WIDTH-1:0] din,

    input re,
    output [WIDTH-1:0] dout,

    output full,
    output empty,

    output almost_full,
    output almost_empty,

    output prog_full,
    output prog_empty,

    output overflow,
    output underflow,

    output rd_rst_busy,
    output wr_rst_busy,

    output [READ_DATA_COUNT_WIDTH-1:0] read_count,
    output [READ_DATA_COUNT_WIDTH-1:0] write_count
);

  function bit[7:0] hex_to_str(x);
    return ((x == 0) ? "0"  : (x == 1) ? "1"  : (x == 2) ? "2"  : (x == 3) ? "3" :
	    (x == 4) ? "4"  : (x == 5) ? "5"  : (x == 6) ? "6"  : (x == 7) ? "7" :
	    (x == 8) ? "8"  : (x == 9) ? "9"  : (x == 10) ? "A" : (x == 11) ? "B" :
	    (x == 12) ? "C" : (x == 13) ? "D" : (x == 14) ? "E" : (x == 15) ? "F" :
	    "?" );
  endfunction


  localparam logic [15:0] feature_bits = {
    3'b0,
    `TEST_BO(DATA_VALID),
    `TEST_BO(ALMOST_EMPTY),
    `TEST_BO(READ_DATA_COUNT_WIDTH > 0),
    `TEST_BO(PROG_EMPTY_THRESH > 0),
    `TEST_BO(UNDERFLOW),
    3'b0,
    `TEST_BO(WRITE_ACK),
    `TEST_BO(ALMOST_FULL),
    `TEST_BO(WRITE_DATA_COUNT_WIDTH > 0),
    `TEST_BO(PROG_FULL_THRESH > 0),
    `TEST_BO(OVERFLOW)
  };

  xpm_fifo_sync #(
      .DOUT_RESET_VALUE("0"),
      .ECC_MODE("no_ecc"),
      .FIFO_MEMORY_TYPE("auto"),
      .FIFO_READ_LATENCY(READ_LATENCY),
      .FIFO_WRITE_DEPTH(DEPTH),
      .FULL_RESET_VALUE(0),
      .PROG_EMPTY_THRESH(PROG_EMPTY_THRESH),
      .PROG_FULL_THRESH(PROG_FULL_THRESH),
      .RD_DATA_COUNT_WIDTH(READ_DATA_COUNT_WIDTH),
      .READ_DATA_WIDTH(WIDTH),
      .READ_MODE("std"),
      .SIM_ASSERT_CHK(1),
      .USE_ADV_FEATURES({hex_to_str(feature_bits[15:12]),
			 hex_to_str(feature_bits[11:8]),
			 hex_to_str(feature_bits[7:4]),
			 hex_to_str(feature_bits[3:0]) }),
      .WAKEUP_TIME(0),
      .WRITE_DATA_WIDTH(WIDTH),
      .WR_DATA_COUNT_WIDTH(WRITE_DATA_COUNT_WIDTH)
  ) fifo (
      .wr_clk(clk),
      .rst(rst),
      .almost_full(almost_full),
      .almost_empty(almost_empty),
      .data_valid(data_valid),
      .din(din),
      .dout(dout),
      .empty(empty),
      .full(full),
      .prog_full(prog_full),
      .prog_empty(prog_empty),
      .rd_en(re),
      .rd_rst_busy(rd_rst_busy),
      .wr_en(we),
      .wr_rst_busy(wr_rst_busy),
      .sleep(sleep)
  );

endmodule


