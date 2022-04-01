`timescale 1ns / 1ps

module piradip_cdc_auto_word #(
    parameter integer WIDTH = 32,
    parameter integer STAGES = 4,
    parameter RESET_VAL = 0
) (
    input rst,
    input src_clk,
    input [WIDTH-1:0] src_data,
    input src_send,
    
    input dst_clk,
    output [WIDTH-1:0] dst_data,
    output dst_update
);
    
    logic reg_ready;
    assign dst_data = reg_ready ? dst_data_cdc : RESET_VAL;
    logic [WIDTH-1:0] dst_data_cdc;
    
    always @(posedge dst_clk)
    begin
        reg_ready = rst ? 1'b0 :
            ~reg_ready ? dst_update :
            1'b1;
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
        .dest_req(dst_update),
        
        .src_clk(src_clk),
        .src_in(src_data),
        .src_send(src_send)
    );
endmodule

module piradip_cdc_auto_reg #(
    parameter integer WIDTH = 32,
    parameter integer STAGES = 4
) (
    input rst,
    
    input src_clk,
    input [WIDTH-1:0] src_data,

    input dst_clk,
    output [WIDTH-1:0] dst_data,
    output dst_update
);
    logic src_send;
    logic last_rst;
    logic [WIDTH-1:0] last_data;

    assign src_send = (last_rst != rst) || (last_data != src_data);    
    
    always @(posedge src_clk)
    begin
        last_rst <= rst;
        last_data <= src_data;
    end

    piradip_cdc_auto_word #(
        .WIDTH(WIDTH),
        .STAGES(STAGES)
    ) cdc (
        .*
    );
endmodule
