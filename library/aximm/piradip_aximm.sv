`timescale 1ns / 1ps

`include "piradip_axi4.svh"

		
interface axi4mm #(
        parameter integer ADDR_WIDTH    = 32,
        parameter integer DATA_WIDTH    = 32,
		parameter integer ID_WIDTH  	= 1,
        parameter integer AWUSER_WIDTH	= 0,
		parameter integer ARUSER_WIDTH	= 0,
		parameter integer WUSER_WIDTH	= 0,
		parameter integer RUSER_WIDTH	= 0,
		parameter integer BUSER_WIDTH	= 0
    ) (
        input logic clk,
        input logic resetn
    );
    localparam STRB_WIDTH=(DATA_WIDTH/8);
        
    logic  aclk;
    logic  aresetn;
    logic [ID_WIDTH-1 : 0] awid;
    logic [ADDR_WIDTH-1 : 0] awaddr;
    logic [7 : 0] awlen;
    logic [2 : 0] awsize;
    logic [1 : 0] awburst;
    logic  awlock;
    logic [3 : 0] awcache;
    logic [2 : 0] awprot;
    logic [3 : 0] awqos;
    logic [AWUSER_WIDTH-1 : 0] awuser;
    logic  awvalid;
    logic  awready;
    logic [DATA_WIDTH-1 : 0] wdata;
    logic [DATA_WIDTH/8-1 : 0] wstrb;
    logic  wlast;
    logic [WUSER_WIDTH-1 : 0] wuser;
    logic  wvalid;
    logic  wready;
    logic [ID_WIDTH-1 : 0] bid;
    logic [1 : 0] bresp;
    logic [BUSER_WIDTH-1 : 0] buser;
    logic  bvalid;
    logic  bready;
    logic [ID_WIDTH-1 : 0] arid;
    logic [ADDR_WIDTH-1 : 0] araddr;
    logic [7 : 0] arlen;
    logic [2 : 0] arsize;
    logic [1 : 0] arburst;
    logic  arlock;
    logic [3 : 0] arcache;
    logic [2 : 0] arprot;
    logic [3 : 0] arqos;
    logic [ARUSER_WIDTH-1 : 0] aruser;
    logic  arvalid;
    logic  arready;
    logic [ID_WIDTH-1 : 0] rid;
    logic [DATA_WIDTH-1 : 0] rdata;
    logic [1 : 0] rresp;
    logic  rlast;
    logic [RUSER_WIDTH-1 : 0] ruser;
    logic  rvalid;
    logic  rready;
    
    assign aclk = clk;
    assign aresetn = resetn;

endinterface
