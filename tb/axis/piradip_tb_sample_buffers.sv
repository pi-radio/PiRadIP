`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/28/2022 04:18:32 PM
// Design Name: 
// Module Name: piradip_tb_sample_buffers
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

module piradip_tb_sample_buffers(
    );
    wire clk;
    reg rstn;
    
    wire stream_clk;
    
    localparam MEMORY_ADDR_WIDTH = 10;
    localparam MEMORY_DATA_WIDTH = 32;
    localparam STREAM_WIDTH=256;

    piradip_tb_clkgen mm_clk_gen(.clk(clk));
    piradip_tb_clkgen #(.HALF_PERIOD(1)) stream_clk_gen(.clk(stream_clk));
        
    axi4mm axi4_data(.clk(clk), .resetn(rstn));
    
    axi4mm_lite ctrl(.clk(clk), .resetn(rstn));
    axi4mm #(.ADDR_WIDTH(MEMORY_ADDR_WIDTH)) memory(.clk(clk), .resetn(rstn));
    axi4s #(.WIDTH(256)) stream(.clk(stream_clk), .resetn(rstn));
    
    piradip_tb_axilite_manager control_manager(.aximm(ctrl));
    piradip_tb_aximm_manager memory_manager(.aximm(memory));
    
    piradip_axis_sample_buffer_out sample_buffer ( 
            .axilite(ctrl.SUBORDINATE),
            .aximm(memory.SUBORDINATE),
            .stream_out(stream.MANAGER) 
        );
        
    integer i;
    
    initial 
    begin
        rstn <= 0;
        
        mm_clk_gen.sleep(5);
        
        rstn <= 1;
        
        mm_clk_gen.sleep(5);
        
        for (i = 0; i < 256; i++) begin
            memory_manager.write_faf(4*i, { { i[5:0], 2'd3 },  { i[5:0], 2'd2 },  { i[5:0], 2'd1 },  { i[5:0], 2'd0 } });
        end

        control_manager.write(0, 3);

        memory_manager.sync();

        for (i = 0; i < 256; i++) begin
            logic [31:0] r;
            memory_manager.read(4*i, r);
            assert(r == { { i[5:0], 2'd3 },  { i[5:0], 2'd2 },  { i[5:0], 2'd1 },  { i[5:0], 2'd0 } });
        end

        
        
        
        $finish;
    end    
    
endmodule
