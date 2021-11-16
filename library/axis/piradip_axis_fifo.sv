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

/* Simple, Symetric and Synchronous fifo */
module piradip_axis_fifo_sss #(
        parameter integer DEPTH=32
    ) (
        input aclk,
        input aresetn,
        axis_simple s_axis,
        axis_simple m_axis
    );
    
    localparam TID=1'b0;
    localparam TUSER=1'b0;
    localparam TDEST=0;
    
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
        .TDATA_WIDTH(s_axis.WIDTH),
        .TDEST_WIDTH(1),
        .TID_WIDTH(1),
        .TUSER_WIDTH(1),
        .USE_ADV_FEATURES("1000"),
        .WR_DATA_COUNT_WIDTH(1)
    ) xpm_fifo (
        .s_aclk(aclk),
        .s_aresetn(aresetn),
        .s_axis_tready(s_axis.tready),
        .s_axis_tdata(s_axis.tdata),
        .s_axis_tlast(s_axis.tlast),
        .s_axis_tvalid(s_axis.tvalid),
        .s_axis_tdest(TDEST),
        .s_axis_tid(TID),
        .s_axis_tkeep(s_axis.BYTE_MASK),
        .s_axis_tstrb(s_axis.BYTE_MASK),
        .s_axis_tuser(TUSER),
        
        .m_aclk(aclk),
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
