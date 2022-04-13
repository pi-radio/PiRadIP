`timescale 1ns / 1ps

module piradspi_tb_engine();
    wire clk;
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    reg rstn;
    
    wire sclk, mosi;
    reg miso;
    
    localparam SEL_WIDTH = 5;
    wire sel_active;
    wire [SEL_WIDTH-1:0] chip_selects;
    wire cmd_completed;

    axis_simple #(.WIDTH(engine.CMD_FIFO_WIDTH)) m2f_cmd();
    axis_simple #(.WIDTH(engine.DATA_FIFO_WIDTH)) m2f_mosi();
    axis_simple #(.WIDTH(engine.DATA_FIFO_WIDTH)) f2s_miso();

    piradspi_fifo_engine #(
	    .SEL_MODE(1),
        .SEL_WIDTH(SEL_WIDTH)
    ) engine (
        .clk(clk),
        .rstn(rstn),
        .axis_cmd(m2f_cmd.SUBORDINATE),
        .axis_mosi(m2f_mosi.SUBORDINATE),
        .axis_miso(f2s_miso.MANAGER),
        .cmd_completed(cmd_completed),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(chip_selects),
        .sel_active(sel_active)
    );

    piradip_util_axis_master #(.WIDTH(engine.CMD_FIFO_WIDTH)) cmd_in(.clk(clk_gen.clk), .aresetn(rstn), .name("CMD"), .masterout(m2f_cmd.MANAGER));
    piradip_util_axis_master #(.WIDTH(engine.DATA_FIFO_WIDTH)) mosi_in(.clk(clk_gen.clk), .aresetn(rstn), .name("MOSI"), .masterout(m2f_mosi.MANAGER));
    piradip_util_axis_slave  #(.WIDTH(engine.DATA_FIFO_WIDTH)) miso_out(.clk(clk_gen.clk), .aresetn(rstn), .name("MISO"), .slavein(f2s_miso.SUBORDINATE));

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

    module command_builder(piradspi_support support);
        task automatic send(
            input int dev,
            input int xfer_len,
            input logic cpol, 
            input logic cpha, 
            input int sclk_cycles=1,
            input int wait_start=1,
            input int csn_to_sclk_cycles = 5,
            input int sclk_to_csn_cycles = 5
            );
            
            int id = cmd_count;
            cmd_count = cmd_count + 1;
    
            cmd_in.send_one(support.build_command(dev, xfer_len, id, cpol, cpha, sclk_cycles,
                wait_start, csn_to_sclk_cycles, sclk_to_csn_cycles));        
        endtask
    endmodule

    command_builder commands(engine.engine.support);
        
    initial 
    begin
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;
        miso <= 0;

        clk_gen.sleep(5);
        
        rstn <= 1;
 
        clk_gen.sleep(5);

        commands.send(0, 64, 0, 0);
        commands.send(1, 64, 1, 0);
        commands.send(2, 64, 0, 1);
        commands.send(3, 64, 1, 1);
        commands.send(4, 24, 0, 0);
        commands.send(0, 64, 0, 0);    
        
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
