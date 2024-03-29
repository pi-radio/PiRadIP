`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10/15/2021 01:24:25 PM
// Design Name:
// Module Name: piradspi_axis_fifo
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

module piradip_axis_gearbox #(
    parameter integer DEPTH = 16,
    parameter integer PROG_FULL_THRESH = 0
) (
    axi4s.SUBORDINATE in,
    axi4s.MANAGER out
);
  /* WARNING, not handling TLAST, TDEST, TUSER, etc */

  localparam integer FIFO_WIDTH = $bits(in.tdata);

  logic sleep;
  logic full, almost_full, prog_full;
  logic empty, almost_empty, prog_empty;
  logic overflow, underflow;
  logic rd_rst_busy, wr_rst_busy;
  logic read_count, write_count;

  logic we, re;

  assign sleep = 1'b0;
  assign we = in.tvalid & in.tready;
  assign re = (out.tready | ~out.tvalid) & ~empty;

  assign in.tready = wr_rst_busy ? 1'b0 : PROG_FULL_THRESH ? ~prog_full : ~almost_full;


  always @(posedge out.aclk) begin
    if (~out.aresetn || rd_rst_busy) begin
      out.tvalid <= 1'b0;
    end else begin
      if (out.tvalid) begin
        out.tvalid <= out.tready ? re : 1'b1;
      end else begin
        out.tvalid <= re;
      end
    end
  end

  assign out.tlast = 0;
  assign out.tuser = 0;
  assign out.tdest = 0;

  piradip_sync_fifo #(
      .PROG_FULL_THRESH(PROG_FULL_THRESH),
      .ALMOST_FULL(PROG_FULL_THRESH ? 0 : 1),
      .WIDTH(FIFO_WIDTH),
      .DEPTH(DEPTH)
  ) fifo (
      .clk(in.aclk),
      .rst(~in.aresetn),
      .sleep(sleep),
      .we(we),
      .din(in.tdata),
      .re(re),
      .full(full),
      .empty(empty),
      .dout(out.tdata),
      .almost_full(almost_full),
      .almost_empty(almost_empty),
      .prog_full(prog_full),
      .prog_empty(prog_empty),
      .overflow(overflow),
      .underflow(underflow),
      .rd_rst_busy(rd_rst_busy),
      .wr_rst_busy(wr_rst_busy),
      .read_count(read_count),
      .write_count(write_count)
  );
endmodule // piradip_axis_gearbox

/*
module piradip_axis_fifo #(
    parameter integer DEPTH = 2
) (
    axi4s.SUBORDINATE in,
    axi4s.MANAGER out
);
  localparam IN_DATA_WIDTH = stream_in.data_width();
  localparam OUT_DATA_WIDTH = stream_out.data_width();

  logic rst;
  logic rd_reset_busy, wr_reset_busy;
  logic wren, rden;
  
  always_comb rst = ~in.aresetn | ~out.aresetn;

  always_comb wren = ~wr_reset_busy & in.tvalid;
  always_comb rden = ~rd_reset_busy & out.tready;
  
  xpm_fifo_async #(
   .CASCADE_HEIGHT(0),        // DECIMAL
   .CDC_SYNC_STAGES(2),       // DECIMAL
   .DOUT_RESET_VALUE("0"),    // String
   .ECC_MODE("no_ecc"),       // String
   .FIFO_MEMORY_TYPE("auto"), // String
   .FIFO_READ_LATENCY(1),     // DECIMAL
   .FIFO_WRITE_DEPTH(2048),   // DECIMAL
   .FULL_RESET_VALUE(0),      // DECIMAL
   .PROG_EMPTY_THRESH(10),    // DECIMAL
   .PROG_FULL_THRESH(10),     // DECIMAL
   .RD_DATA_COUNT_WIDTH(1),   // DECIMAL
   .READ_DATA_WIDTH(32),      // DECIMAL
   .READ_MODE("std"),         // String
   .RELATED_CLOCKS(0),        // DECIMAL
   .SIM_ASSERT_CHK(0),        // DECIMAL; 0=disable simulation messages, 1=enable simulation messages
   .USE_ADV_FEATURES("0707"), // String
   .WAKEUP_TIME(0),           // DECIMAL
   .WRITE_DATA_WIDTH(32),     // DECIMAL
   .WR_DATA_COUNT_WIDTH(1)    // DECIMAL
)
  fifo_inst (
   //.almost_empty(almost_empty),  
   //.almost_full(almost_full),    
   //.dbiterr(dbiterr),
   //.empty(empty),
   //.full(full),
   //.overflow(overflow),
   //.prog_empty(prog_empty),
   //.prog_full(prog_full),
   //.rd_data_count(rd_data_count),
   //.sbiterr(sbiterr),
   //.underflow(underflow),
   //.wr_ack(wr_ack),
   //.wr_data_count(wr_data_count),
   //.injectdbiterr(injectdbiterr),
   //.injectsbiterr(injectsbiterr),

   .rst(rst),
   .sleep(1b0),
	     
   .rd_clk(out.aclk),
   .rd_rst_busy(rd_reset_busy),
   .rd_en(rden),
   .data_valid(out.tvalid),       
   .dout(out.tdata),

   .wr_clk(in.aclk),
   .wr_rst_busy(wr_reset_busy),
   .din(in.tdata),
   .wr_en(wren)
);  
  
endmodule
*/

/* Simple, Symetric and Synchronous fifo */
module piradip_axis_fifo_sss #(
    parameter integer DEPTH = 32
) (
    axis_simple s_axis,
    axis_simple m_axis
);

  localparam TID = 1'b0;
  localparam TUSER = 1'b0;
  localparam TDEST = 0;
  localparam WIDTH = $bits(s_axis.tdata);
  localparam BYTE_MASK = {{WIDTH / 8} {1'b1}};

  xpm_fifo_axis #(
      .CDC_SYNC_STAGES(2),
      .CLOCKING_MODE("common_clock"),
      .ECC_MODE("no_ecc"),
      .FIFO_DEPTH(DEPTH),
      .FIFO_MEMORY_TYPE("auto"),
      .PACKET_FIFO("false"),
      .PROG_EMPTY_THRESH(10),
      .PROG_FULL_THRESH(10),
      .RD_DATA_COUNT_WIDTH(1),
      .RELATED_CLOCKS(0),
      .SIM_ASSERT_CHK(0),
      .TDATA_WIDTH(WIDTH),
      .TDEST_WIDTH(1),
      .TID_WIDTH(1),
      .TUSER_WIDTH(1),
      .USE_ADV_FEATURES("1000"),
      .WR_DATA_COUNT_WIDTH(1)
  ) xpm_fifo (
      .s_aclk(s_axis.aclk),
      .s_aresetn(s_axis.aresetn),
      .s_axis_tready(s_axis.tready),
      .s_axis_tdata(s_axis.tdata),
      .s_axis_tlast(s_axis.tlast),
      .s_axis_tvalid(s_axis.tvalid),
      .s_axis_tdest(TDEST),
      .s_axis_tid(TID),
      .s_axis_tkeep(BYTE_MASK),
      .s_axis_tstrb(BYTE_MASK),
      .s_axis_tuser(TUSER),

      .m_aclk(m_axis.aclk),
      .m_axis_tready(m_axis.tready),
      .m_axis_tdata(m_axis.tdata),
      .m_axis_tlast(m_axis.tlast),
      .m_axis_tvalid(m_axis.tvalid),
      //.m_axis_tdest(m_tdest),
      //.m_axis_tid(m_tid),
      //.m_axis_tkeep(m_tkeep),
      //.m_axis_tstrb(m_tstrb),
      //.m_axis_tuser(m_axis_tuser),

      /*
                                .almost_empty_axis(almost_empty_axis),
                                .almost_full_axis(almost_full_axis),
                                .dbiterr_axis(dbiterr_axis),
                                .prog_empty_axis(prog_empty_axis),
                                .prog_full_axis(prog_full_axis),
                                .rd_data_count_axis(rd_data_count_axis),
                                .sbiterr_axis(sbiterr_axis),
                                .wr_data_count_axis(wr_data_count_axis),
                                */
      .injectdbiterr_axis(1'b0),
      .injectsbiterr_axis(1'b0)
  );


endmodule
