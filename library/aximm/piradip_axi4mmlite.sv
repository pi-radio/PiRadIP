`timescale 1ns / 1ps

interface axi4mm_lite 
  #(
    parameter integer ADDR_WIDTH=8,
    parameter integer DATA_WIDTH=32
    ) 
   (
    input logic clk, 
    input logic resetn
    );
   import piradip_axi4::*;
   
   typedef logic [DATA_WIDTH-1:0]     data_t;
   typedef logic [DATA_WIDTH/8-1:0]   strb_t;
   typedef logic [ADDR_WIDTH-1:0]     addr_t;
   
   logic            aclk;
   logic            aresetn;
   addr_t           awaddr;
   axi_prot_t       awprot;
   logic            awvalid;
   logic            awready;
   data_t           wdata;
   strb_t           wstrb;
   logic            wvalid;
   logic            wready;
   axi_resp_t       bresp;
   logic            bvalid;
   logic            bready;
   addr_t           araddr;
   axi_prot_t       arprot;
   logic            arvalid;
   logic            arready;
   data_t           rdata;
   axi_resp_t       rresp;
   logic            rvalid;
   logic            rready;

   assign aclk = clk;
   assign aresetn = resetn;
   
   modport MANAGER(input aclk, aresetn,
                   awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid, 
                   output awaddr, awprot, awvalid, wdata, wstrb,
                   wvalid, bready, araddr, arprot, arvalid, rready);

   modport SUBORDINATE(output awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid,
                       input awaddr, awprot, awvalid, wdata, wstrb,
                       wvalid, bready, araddr, arprot, arvalid, rready, 
                       aclk, aresetn);
endinterface

