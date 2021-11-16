`timescale 1ns / 1ps

interface axis_simple #(
        parameter WIDTH=32
    ) (
        input clk,
        input resetn
    );
    localparam BYTE_WIDTH = WIDTH/8;
    localparam BYTE_MASK = {{BYTE_WIDTH}{1'b1}};
    
    assign aclk = clk;
    assign aresetn = resetn;
    
    logic aclk, aresetn;
    logic tready, tvalid, tlast;
    logic [WIDTH-1:0] tdata;
    
    modport SUBORDINATE (input tvalid, tlast, tdata, output tready, aclk, aresetn);
    modport MANAGER (output tvalid, tlast, tdata, aclk, aresetn, input tready);
endinterface

interface axi4s #(
        parameter WIDTH=32,
        parameter ID_WIDTH=0,
        parameter DEST_WIDTH=0,
        parameter USER_WIDTH=0
    ) (
        input clk,
        input resetn
    );
    localparam BYTE_WIDTH = WIDTH/8;
    localparam BYTE_MASK = {{BYTE_WIDTH}{1'b1}};
    
    assign aclk = clk;
    assign aresetn = resetn;
    
    logic aclk, aresetn;
    logic tready, tvalid, tlast;
    logic [WIDTH-1:0] tdata;
    logic [BYTE_WIDTH-1:0] tstrb;
    logic [BYTE_WIDTH-1:0] tkeep;
    logic [ID_WIDTH-1:0] tid;
    logic [DEST_WIDTH-1:0] tdest;
    logic [USER_WIDTH-1:0] tuser;
    
    modport SUBORDINATE (input tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser, output tready, aclk, aresetn);
    modport MANAGER (output tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser, aclk, aresetn, input tready);
endinterface
