`timescale 1ns / 1ps

module piradip_cdc_auto_word #(
    parameter integer WIDTH = 32,
    parameter integer STAGES = 4
) (
    input src_clk,
    input [WIDTH-1:0] src_data,
    input src_send,
    
    input dst_clk,
    output dst_data,
    output dst_update
);
    xpm_cdc_handshake #(
        .DEST_EXT_HSK(1'b0),
        .DEST_SYNC_FF(STAGES),
        .INIT_SYNC_FF(1),
        .SIM_ASSERT_CHECK(1),
        .WIDTH(WIDTH)
    ) cdc (
        .dest_clk(dst_clk),
        .dest_out(dst_data),
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
    input src_clk,
    input [WIDTH-1:0] src_data,

    input dst_clk,
    output dst_data,
    output dst_update
);
    reg [WIDTH-1:0] last_data;
    
    always @(posedge src_clk)
    begin
        last_data <= src_data;
    end

    xpm_cdc_handshake #(
        .DEST_EXT_HSK(1'b0),
        .DEST_SYNC_FF(STAGES),
        .INIT_SYNC_FF(1),
        .SIM_ASSERT_CHECK(1),
        .WIDTH(WIDTH)
    ) cdc (
        .dest_clk(dst_clk),
        .dest_out(dst_data),
        .dest_req(dst_update),
        
        .src_clk(src_clk),
        .src_in(src_data),
        .src_send(last_data != src_data)
    );
endmodule
