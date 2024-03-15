`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 08/27/2019 10:58:41 AM
// Design Name: 
// Module Name: AXIRandomStream
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

module RingOscillator #
(
    parameter integer WIDTH = 16
)
(
    input wire clk,
    output reg [WIDTH-1:0] out
);
    genvar i;
`ifdef XILINX_SIMULATOR
    for (i = 0; i < WIDTH/32; i=i+1) 
    begin
        always @(posedge clk) out[32*i+:32] <= $urandom();
    end
`else  
    (* dont_touch = "yes", allow_combinatorial_loops="true" *) 
    wire [WIDTH - 1:0] osc, osc_r, osc_l;
    
    assign osc_r = { osc[0], osc[WIDTH-1:1] };
    assign osc_l = { osc[WIDTH-2:0], osc[WIDTH-1] };
    
    (* dont_touch = "yes" *) always @(posedge clk) out <= osc;
    
    for (i = 0; i < WIDTH; i = i + 1) 
    begin
        (* dont_touch = "yes" *) LUT3 #(.INIT((i == 0) ? 8'b0110_1001 : 8'b1001_0110)) 
        lut(.O(osc[i]),
            .I0(osc[i]),
            .I1(osc_l[i]),
            .I2(osc_r[i]));
    end
`endif    
endmodule



(* keep_hierarchy = "yes" *) module AXIRandomStream #
(
		parameter integer C_AXI_STREAM_TDATA_WIDTH	= 256
)
(
        input wire axis_aclk,
        input wire axis_aresetn,
        
		output wire  axis_rand_out_tvalid,
		output wire [C_AXI_STREAM_TDATA_WIDTH-1 : 0] axis_rand_out_tdata,
		input wire  axis_rand_out_tready
);
    localparam D = (C_AXI_STREAM_TDATA_WIDTH == 8) ? 8'h06 :
       (C_AXI_STREAM_TDATA_WIDTH == 16) ? 16'h4001 :
       (C_AXI_STREAM_TDATA_WIDTH == 32) ? 32'h00004001 :
       (C_AXI_STREAM_TDATA_WIDTH == 64) ? 64'h00000000_00000014 :
       (C_AXI_STREAM_TDATA_WIDTH == 128) ? 128'h2000_0001 :
       (C_AXI_STREAM_TDATA_WIDTH == 256) ? 256'h10000000_00000000_00000000_00000001 : 0;
       
    
    genvar i;
    
    wire [C_AXI_STREAM_TDATA_WIDTH-1:0] osc_out;
    
    RingOscillator #(.WIDTH(C_AXI_STREAM_TDATA_WIDTH)) ring(.clk(axis_aclk),.out(osc_out));
    
    reg [C_AXI_STREAM_TDATA_WIDTH-1:0] lhca;
    
    always @(posedge axis_aclk) lhca <= (~axis_aresetn) ?  {C_AXI_STREAM_TDATA_WIDTH{1'b0}}  : (lhca & D) ^ osc_out ^ { 0, lhca[C_AXI_STREAM_TDATA_WIDTH-1:1] } ^ { lhca[C_AXI_STREAM_TDATA_WIDTH-2:0], 0 };
    
    assign axis_rand_out_tvalid = axis_aresetn;
    assign axis_rand_out_tdata = lhca;            
endmodule
