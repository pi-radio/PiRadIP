`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/14/2021 01:17:06 PM
// Design Name: 
// Module Name: piradspi_tb_engine
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
module piradspi_tb_engine_on_board(

    );
    typedef piradspi_types #(
        .REG_WIDTH(32)
    ) types_inst; 

    wire clk;
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    reg rstn;
    
    wire sclk, mosi;
    reg miso;
    
    wire [4:0] chip_selects;
    wire cmd_completed;
    
    piradip_util_axis_master #(.WIDTH(types_inst::CMD_FIFO_WIDTH)) cmd_in(.clk(clk_gen.clk), .aresetn(rstn), .name("CMD"));
    piradip_util_axis_master #(.WIDTH(types_inst::DATA_FIFO_WIDTH)) mosi_in(.clk(clk_gen.clk), .aresetn(rstn), .name("MOSI"));
    piradip_util_axis_slave  #(.WIDTH(types_inst::DATA_FIFO_WIDTH)) miso_out(.clk(clk_gen.clk), .aresetn(rstn), .name("MISO"));
        
    wire [types_inst::CMD_FIFO_WIDTH-1:0] cmd_out_data;

    wire cmd_out_ready, cmd_out_valid, cmd_out_last;

    wire [types_inst::DATA_FIFO_WIDTH-1:0] mosi_out_data;
    
    wire mosi_out_ready, mosi_out_valid, mosi_out_last;

    wire [types_inst::DATA_FIFO_WIDTH-1:0] miso_in_data;
    wire miso_in_ready, miso_in_valid, miso_in_last;
    
    types_inst::command_u_t cmd;

    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::CMD_FIFO_WIDTH)
    ) cmd_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_tdata(cmd_in.tdata),
        .s_tready(cmd_in.tready),
        .s_tvalid(cmd_in.tvalid),
        .s_tlast(cmd_in.tlast),
        .m_tdata(cmd_out_data),
        .m_tready(cmd_out_ready),
        .m_tvalid(cmd_out_valid),
        .m_tlast(cmd_out_last)
    );

    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::DATA_FIFO_WIDTH)
    ) mosi_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_tdata(mosi_in.tdata),
        .s_tready(mosi_in.tready),
        .s_tvalid(mosi_in.tvalid),
        .s_tlast(mosi_in.tlast),
        .m_tdata(mosi_out_data),
        .m_tready(mosi_out_ready),
        .m_tvalid(mosi_out_valid),
        .m_tlast(mosi_out_last)
    );
    
    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::DATA_FIFO_WIDTH)
    ) miso_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_tdata(miso_in_data),
        .s_tready(miso_in_ready),
        .s_tvalid(miso_in_valid),
        .s_tlast(miso_in_last),
        .m_tdata(miso_out.tdata),
        .m_tready(miso_out.tready),
        .m_tvalid(miso_out.tvalid),
        .m_tlast(miso_out.tlast)
    );
    
    piradspi_engine #(
        .SEL_MODE(1), 
        .SEL_WIDTH(5)
    ) engine (
        .clk(clk_gen.clk),
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(chip_selects),
        .cmd_completed(cmd_completed),
        
        .cmd_valid(cmd_out_valid),
        .cmd_ready(cmd_out_ready),
        .cmd_data(cmd_out_data),
        .cmd_tlast(cmd_out_last),
        
        .mosi_valid(mosi_out_valid),
        .mosi_ready(mosi_out_ready),
        .mosi_data(mosi_out_data),
        .mosi_tlast(mosi_out_last),
        
        .miso_valid(miso_in_valid),
        .miso_ready(miso_in_ready),
        .miso_data(miso_in_data),
        .miso_tlast(miso_in_last)
    );


    piradio_v2_tb_spi_decoder v2_spi_decoder(.rstn(rstn),
        .mosi(mosi),
        .miso(miso),
        .sclk(sclk),
        .card_sel(chip_selects));

        
    initial 
    begin
        rstn <= 0;
        miso <= 0;



        cmd.c.cmd.cpol <= 0;
        cmd.c.cmd.cpha <= 0;
        cmd.c.cmd.id <= 67;
        cmd.c.cmd.device <= 3;
        cmd.c.cmd.sclk_cycles <= 1;
        cmd.c.cmd.wait_start <= 1;
        cmd.c.cmd.csn_to_sclk_cycles <= 5;
        cmd.c.cmd.sclk_to_csn_cycles <= 5;
        cmd.c.cmd.xfer_len <= 64;
        cmd.c.pad <= 0;
        
        clk_gen.sleep(5);
        
        rstn <= 1;
 
        clk_gen.sleep(5);
        
        cmd_in.send_one(cmd.data);
        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);
        
        wait(cmd_completed == 1);
        
        
       
        clk_gen.sleep(10);
        $finish;
    end
        
    
endmodule
