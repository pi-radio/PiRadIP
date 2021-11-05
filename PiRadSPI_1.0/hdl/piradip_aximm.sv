`timescale 1ns / 1ps

`include "piradip_aximm.svh"

interface axi4mm #(
        parameter integer ADDR_WIDTH=8,
        parameter integer DATA_WIDTH=32
    ) (
        input logic aclk,
        input logic aresetn
    );
    localparam STRB_WIDTH=(DATA_WIDTH/8);
    
    /* TODO FINISH */
    
    logic [ADDR_WIDTH-1 : 0] awaddr;
    logic [2 : 0] awprot;
    logic awvalid;
    logic awready;
    logic [DATA_WIDTH-1 : 0] wdata;
    logic [STRB_WIDTH-1 : 0] wstrb;
    logic wvalid;
    logic wready;
    logic [1 : 0] bresp;
    logic bvalid;
    logic bready;
    logic [ADDR_WIDTH-1 : 0] araddr;
    logic [2 : 0] arprot;
    logic arvalid;
    logic arready;
    logic [DATA_WIDTH-1 : 0] rdata;
    logic [1 : 0] rresp;
    logic rvalid;
    logic rready;    
endinterface

/*
module xilinx_axilite_adapter #(
    parameter ADDR_WIDTH=8,
    parameter DATA_WIDTH=32
    ) (
    axi4mm_lite axilite_iface,
    input wire  aclk,
    input wire  aresetn,
    input wire [ADDR_WIDTH-1 : 0] awaddr,
    input wire [2 : 0] awprot,
    input wire  awvalid,
    output wire  awready,
    input wire [DATA_WIDTH-1 : 0] wdata,
    input wire [(DATA_WIDTH/8)-1 : 0] wstrb,
    input wire  wvalid,
    output wire  wready,
    output wire [1 : 0] bresp,
    output wire  bvalid,
    input wire  bready,
    input wire [ADDR_WIDTH-1 : 0] araddr,
    input wire [2 : 0] arprot,
    input wire  arvalid,
    output wire  arready,
    output wire [DATA_WIDTH-1 : 0] rdata,
    output wire [1 : 0] rresp,
    output wire  rvalid,
    input wire  rready    
    );
    
endmodule

`define PIRADIP_GLUE_ASSIGNMENT(prefix, iface, signal) .prefix``_signal(iface.signal)
`define PIRADIP_GLUE_AXILITE(prefix, iface) \
    PIRADIP_GLUE_ASSIGNMENT(prefix, iface, aclk)
*/
