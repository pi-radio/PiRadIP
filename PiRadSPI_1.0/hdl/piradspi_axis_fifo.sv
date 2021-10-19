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
        parameter integer WIDTH=32,
        parameter integer DEPTH=32
    ) (
        input aclk,
        input aresetn,
        input [WIDTH-1:0] s_tdata,
        output s_tready,
        input s_tvalid,
        input s_tlast,
        output [WIDTH-1:0] m_tdata,
        input m_tready,
        output m_tvalid,
        output m_tlast
    );
    
    localparam TID=1'b0;
    localparam TKEEP={{WIDTH/8}{1'b1}};
    localparam TSTRB={{WIDTH/8}{1'b1}};
    localparam TUSER=1'b0;
    
    xpm_fifo_axis #(
        .CDC_SYNC_STAGES(2),            // DECIMAL
        .CLOCKING_MODE("common_clock"), // String
        .ECC_MODE("no_ecc"),            // String
        .FIFO_DEPTH(DEPTH),              // DECIMAL
        .FIFO_MEMORY_TYPE("auto"),      // String
        .PACKET_FIFO("false"),          // String
        .PROG_EMPTY_THRESH(10),         // DECIMAL
        .PROG_FULL_THRESH(10),          // DECIMAL
        .RD_DATA_COUNT_WIDTH(1),        // DECIMAL
        .RELATED_CLOCKS(0),             // DECIMAL
        .SIM_ASSERT_CHK(0),             // DECIMAL; 0=disable simulation messages, 1=enable simulation messages
        .TDATA_WIDTH(WIDTH),               // DECIMAL
        .TDEST_WIDTH(1),                // DECIMAL
        .TID_WIDTH(1),                  // DECIMAL
        .TUSER_WIDTH(1),                // DECIMAL
        .USE_ADV_FEATURES("1000"),      // String
        .WR_DATA_COUNT_WIDTH(1)         // DECIMAL
    ) xpm_fifo (
        .s_aclk(aclk),
        .s_aresetn(aresetn),
        .s_axis_tready(s_tready),
        .s_axis_tdata(s_tdata),
        .s_axis_tdest(s_tdest),
        .s_axis_tid(TID),
        .s_axis_tkeep(TKEEP),
        .s_axis_tlast(s_tlast),
        .s_axis_tstrb(TSTRB),
        .s_axis_tuser(TUSER),
        .s_axis_tvalid(s_tvalid),
        
        .m_aclk(aclk),
        .m_axis_tready(m_tready),
        .m_axis_tdata(m_tdata),
        //.m_axis_tdest(m_tdest),
        //.m_axis_tid(m_tid),
        //.m_axis_tkeep(m_tkeep),
        .m_axis_tlast(m_tlast),
        //.m_axis_tstrb(m_tstrb),
        //.m_axis_tuser(m_axis_tuser),
        .m_axis_tvalid(m_tvalid),
        
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
