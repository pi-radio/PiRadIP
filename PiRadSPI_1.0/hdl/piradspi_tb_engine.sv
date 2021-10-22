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
module piradspi_tb_engine(

    );
    typedef piradspi_types #(
        .REG_WIDTH(32)
    ) spi_types; 

    wire clk;
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    reg rstn;
    
    wire sclk, mosi;
    reg miso;
    
    wire sel_active;
    wire [4:0] chip_selects;
    wire cmd_completed;
    
    piradip_util_axis_master #(.WIDTH(spi_types::CMD_FIFO_WIDTH)) cmd_in(.clk(clk_gen.clk), .aresetn(rstn), .name("CMD"));
    piradip_util_axis_master #(.WIDTH(spi_types::DATA_FIFO_WIDTH)) mosi_in(.clk(clk_gen.clk), .aresetn(rstn), .name("MOSI"));
    piradip_util_axis_slave  #(.WIDTH(spi_types::DATA_FIFO_WIDTH)) miso_out(.clk(clk_gen.clk), .aresetn(rstn), .name("MISO"));
        
    wire [spi_types::CMD_FIFO_WIDTH-1:0] cmd_out_data;

    wire cmd_out_ready, cmd_out_valid, cmd_out_last;

    wire [spi_types::DATA_FIFO_WIDTH-1:0] mosi_out_data;
    
    wire mosi_out_ready, mosi_out_valid, mosi_out_last;

    wire [spi_types::DATA_FIFO_WIDTH-1:0] miso_in_data;
    wire miso_in_ready, miso_in_valid, miso_in_last;

    piradip_axis_fifo_sss #(
        .WIDTH(spi_types::CMD_FIFO_WIDTH)
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
        .WIDTH(spi_types::DATA_FIFO_WIDTH)
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
        .WIDTH(spi_types::DATA_FIFO_WIDTH)
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
        .sel_active(sel_active),
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
    
    assign sclk_hold = engine.sclk_hold;

    piradip_tb_spi_slave #(
        .WIDTH(64),
        .CPOL(0),
        .CPHA(0),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_00 (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(sel_active && (chip_selects == 0))),
        .name("Slave 00")
    );

    piradip_tb_spi_slave #(
        .WIDTH(64),
        .CPOL(1),
        .CPHA(0),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_10 (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(sel_active && (chip_selects == 1))),
        .name("Slave 10")
    );
 
    piradip_tb_spi_slave #(
        .WIDTH(64),
        .CPOL(0),
        .CPHA(1),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_01 (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(sel_active && (chip_selects == 2))),
        .name("Slave 01")
    ); 

    piradip_tb_spi_slave #(
        .WIDTH(64),
        .CPOL(1),
        .CPHA(1),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_11 (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(sel_active && (chip_selects == 3))),
        .name("Slave 11")
    );
    
    piradip_tb_spi_slave #(
        .WIDTH(24),
        .CPOL(0),
        .CPHA(0),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_00_24bit (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(sel_active && (chip_selects == 4))),
        .name("Slave 00 24 bit")
    ); 
    
    int cmd_submitted;
    int cmd_completions;
    int cmd_pending = cmd_submitted - cmd_completions;
    
    always @(posedge clk_gen.clk)
    begin
        if (~rstn) begin
            cmd_completions <= 0;
        end else if (cmd_completed) begin
            cmd_completions <= cmd_completions + 1;
        end
    end

    int cmd_count = 0;

    task automatic send_command(
        input spi_types::dev_id_t dev,
        input spi_types::xfer_len_t xfer_len,
        input logic cpol, 
        input logic cpha, 
        input spi_types::wait_t sclk_cycles=1,
        input spi_types::wait_t wait_start=1,
        input spi_types::wait_t csn_to_sclk_cycles = 5,
        input spi_types::wait_t sclk_to_csn_cycles = 5
        );
        
        spi_types::command_u_t cmd;
        
        cmd.c.cmd.id = cmd_count;
        cmd_count = cmd_count + 1;
        
        cmd.c.cmd.cpol = cpol;
        cmd.c.cmd.cpha = cpha;
        
        cmd.c.cmd.device = dev;
        cmd.c.cmd.sclk_cycles = sclk_cycles;
        cmd.c.cmd.wait_start = wait_start;
        cmd.c.cmd.csn_to_sclk_cycles = csn_to_sclk_cycles;
        cmd.c.cmd.sclk_to_csn_cycles = sclk_to_csn_cycles;
        cmd.c.cmd.xfer_len = xfer_len;
        cmd.c.pad = 0;
        cmd_in.send_one(cmd.data);        
    endtask
        
    initial 
    begin
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;
        miso <= 0;


        
        clk_gen.sleep(5);
        
        rstn <= 1;
 
        clk_gen.sleep(5);

        send_command(0, 64, 0, 0);
        send_command(1, 64, 1, 0);
        send_command(2, 64, 0, 1);
        send_command(3, 64, 1, 1);
        send_command(4, 24, 0, 0);
        send_command(0, 64, 0, 0);    
        
        // Wait for the commands to all queue
        cmd_in.sync();
        
        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);
        
        // Todo -- write send_event, send_delay, send_event_delay
        wait(cmd_completed == 1);
       
        clk_gen.sleep(40);

        // Make the second command wait for data        
        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);       
        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);            
        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);    

        // 24 bit client
        mosi_in.send_one(32'h11223344);    

        mosi_in.send_one(32'hA5B6A5B6);        
        mosi_in.send_one(32'hBCBCBCBC);  

        wait(cmd_completed == 1);
        
        wait(cmd_completions == 6);
               
        clk_gen.sleep(10);
        $finish;
    end
        
    
endmodule
