`timescale 1ns / 1ps

interface axis_simple #(
        parameter integer WIDTH=32
    ) (
        input logic clk,
        input logic resetn
    );
    localparam BYTE_WIDTH = WIDTH/8;
    localparam BYTE_MASK = {{BYTE_WIDTH}{1'b1}};

    logic aclk, aresetn;
    logic tready, tvalid, tlast;
    logic [WIDTH-1:0] tdata;
    
    assign aclk = clk;
    assign aresetn = resetn;

    modport SUBORDINATE (input tvalid, tlast, tdata, output tready, aclk, aresetn);
    modport MANAGER (output tvalid, tlast, tdata, aclk, aresetn, input tready);
endinterface

interface axi4s #(
        parameter integer WIDTH=32,
        parameter integer ID_WIDTH=0,
        parameter integer DEST_WIDTH=0,
        parameter integer USER_WIDTH=0
    ) (
        input logic clk,
        input logic resetn
    );
    localparam BYTE_WIDTH = WIDTH/8;
    localparam BYTE_MASK = {BYTE_WIDTH{1'b1}};
        
    logic aclk, aresetn;
    logic tready, tvalid, tlast;
    logic [WIDTH-1:0] tdata;
    logic [BYTE_WIDTH-1:0] tstrb;
    logic [BYTE_WIDTH-1:0] tkeep;
    logic [ID_WIDTH-1:0] tid;
    logic [DEST_WIDTH-1:0] tdest;
    logic [USER_WIDTH-1:0] tuser;
    
    assign aclk = clk;
    assign aresetn = resetn;

    
    modport SUBORDINATE (input tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser, output tready, aclk, aresetn);
    modport MANAGER (output tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser, aclk, aresetn, input tready);
endinterface
