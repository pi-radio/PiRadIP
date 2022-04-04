/*`include "piradip_axi4.svh"*/

`timescale 1 ns / 1 ps

`define PIRADIP_PREFIX_ASSIGN(x, prefix)                    .x(prefix``x)
`define PIRADIP_PREFIX_ASSIGN_DIFFERENT(x, prefix, y)       .x(prefix``y)
`define PIRADIP_PREFIX_ALWAYS_COMB_OUT(ifname, x, prefix)   always_comb prefix``x=ifname.x
`define PIRADIP_PREFIX_ALWAYS_COMB_IN(ifname, x, prefix)    always_comb ifname.x=prefix``x
`define PIRADIP_PREFIX_ASSIGN_OUT(ifname, x, prefix)        assign prefix``x=ifname.x
`define PIRADIP_PREFIX_ASSIGN_IN(ifname, x, prefix)         assign ifname.x=prefix``x


`define PIRADIP_AXI4LITE_SUBORDINATE_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm_lite #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const) \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rready, xil_prefix);  
    
`define PIRADIP_AXI4_SUBORDINATE_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ID_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(AWUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ARUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(WUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(RUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(BUSER_WIDTH, xil_prefix_const)  \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, buser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, aruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arready, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, ruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rready, xil_prefix);    

`define PIRADIP_AXI4STREAM_MANAGER_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4s #( \
        `PIRADIP_PREFIX_ASSIGN_DIFFERENT(WIDTH, xil_prefix_const, TDATA_WIDTH) \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, tvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, tdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, tstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, tlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, tready, xil_prefix);

module PiRadIP_StreamBufferOut_v1_0 #(
        parameter integer C_S00_AXI_DATA_WIDTH	= 32,
        parameter integer C_S00_AXI_ADDR_WIDTH	= 4,
        
        // Parameters of Axi Slave Bus Interface S01_AXI
        parameter integer C_S01_AXI_ID_WIDTH	= 1,
        parameter integer C_S01_AXI_DATA_WIDTH	= 32,
        parameter integer C_S01_AXI_ADDR_WIDTH	= 10,
        parameter integer C_S01_AXI_AWUSER_WIDTH	= 0,
        parameter integer C_S01_AXI_ARUSER_WIDTH	= 0,
        parameter integer C_S01_AXI_WUSER_WIDTH	= 0,
        parameter integer C_S01_AXI_RUSER_WIDTH	= 0,
        parameter integer C_S01_AXI_BUSER_WIDTH	= 0,
        
        // Parameters of Axi Master Bus Interface M00_AXIS
        parameter integer C_M00_AXIS_TDATA_WIDTH	= 32,
        parameter integer C_M00_AXIS_START_COUNT	= 32
    ) (
	    input wire trigger,
		input wire  s00_axi_aclk,
		input wire  s00_axi_aresetn,
		input wire [C_S00_AXI_ADDR_WIDTH-1 : 0] s00_axi_awaddr,
		input wire [2 : 0] s00_axi_awprot,
		input wire  s00_axi_awvalid,
		output wire  s00_axi_awready,
		input wire [C_S00_AXI_DATA_WIDTH-1 : 0] s00_axi_wdata,
		input wire [(C_S00_AXI_DATA_WIDTH/8)-1 : 0] s00_axi_wstrb,
		input wire  s00_axi_wvalid,
		output wire  s00_axi_wready,
		output wire [1 : 0] s00_axi_bresp,
		output wire  s00_axi_bvalid,
		input wire  s00_axi_bready,
		input wire [C_S00_AXI_ADDR_WIDTH-1 : 0] s00_axi_araddr,
		input wire [2 : 0] s00_axi_arprot,
		input wire  s00_axi_arvalid,
		output wire  s00_axi_arready,
		output wire [C_S00_AXI_DATA_WIDTH-1 : 0] s00_axi_rdata,
		output wire [1 : 0] s00_axi_rresp,
		output wire  s00_axi_rvalid,
		input wire  s00_axi_rready,
		input wire  s01_axi_aclk,
		input wire  s01_axi_aresetn,
		input wire [C_S01_AXI_ID_WIDTH-1 : 0] s01_axi_awid,
		input wire [C_S01_AXI_ADDR_WIDTH-1 : 0] s01_axi_awaddr,
		input wire [7 : 0] s01_axi_awlen,
		input wire [2 : 0] s01_axi_awsize,
		input wire [1 : 0] s01_axi_awburst,
		input wire  s01_axi_awlock,
		input wire [3 : 0] s01_axi_awcache,
		input wire [2 : 0] s01_axi_awprot,
		input wire [3 : 0] s01_axi_awqos,
		input wire [3 : 0] s01_axi_awregion,
		input wire [C_S01_AXI_AWUSER_WIDTH-1 : 0] s01_axi_awuser,
		input wire  s01_axi_awvalid,
		output wire  s01_axi_awready,
		input wire [C_S01_AXI_DATA_WIDTH-1 : 0] s01_axi_wdata,
		input wire [(C_S01_AXI_DATA_WIDTH/8)-1 : 0] s01_axi_wstrb,
		input wire  s01_axi_wlast,
		input wire [C_S01_AXI_WUSER_WIDTH-1 : 0] s01_axi_wuser,
		input wire  s01_axi_wvalid,
		output wire  s01_axi_wready,
		output wire [C_S01_AXI_ID_WIDTH-1 : 0] s01_axi_bid,
		output wire [1 : 0] s01_axi_bresp,
		output wire [C_S01_AXI_BUSER_WIDTH-1 : 0] s01_axi_buser,
		output wire  s01_axi_bvalid,
		input wire  s01_axi_bready,
		input wire [C_S01_AXI_ID_WIDTH-1 : 0] s01_axi_arid,
		input wire [C_S01_AXI_ADDR_WIDTH-1 : 0] s01_axi_araddr,
		input wire [7 : 0] s01_axi_arlen,
		input wire [2 : 0] s01_axi_arsize,
		input wire [1 : 0] s01_axi_arburst,
		input wire  s01_axi_arlock,
		input wire [3 : 0] s01_axi_arcache,
		input wire [2 : 0] s01_axi_arprot,
		input wire [3 : 0] s01_axi_arqos,
		input wire [3 : 0] s01_axi_arregion,
		input wire [C_S01_AXI_ARUSER_WIDTH-1 : 0] s01_axi_aruser,
		input wire  s01_axi_arvalid,
		output wire  s01_axi_arready,
		output wire [C_S01_AXI_ID_WIDTH-1 : 0] s01_axi_rid,
		output wire [C_S01_AXI_DATA_WIDTH-1 : 0] s01_axi_rdata,
		output wire [1 : 0] s01_axi_rresp,
		output wire  s01_axi_rlast,
		output wire [C_S01_AXI_RUSER_WIDTH-1 : 0] s01_axi_ruser,
		output wire  s01_axi_rvalid,
		input wire  s01_axi_rready,
		input wire  m00_axis_aclk,
		input wire  m00_axis_aresetn,
		output wire  m00_axis_tvalid,
		output wire [C_M00_AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
		output wire [(C_M00_AXIS_TDATA_WIDTH/8)-1 : 0] m00_axis_tstrb,
		output wire  m00_axis_tlast,
		input wire  m00_axis_tready
	);

    `PIRADIP_AXI4LITE_SUBORDINATE_ADAPTER(csr_if, C_S00_AXI_, s00_axi_)
    `PIRADIP_AXI4_SUBORDINATE_ADAPTER(mem_if, C_S01_AXI_, s01_axi_)
    `PIRADIP_AXI4STREAM_MANAGER_ADAPTER(stream_if, C_M00_AXIS_, m00_axis_)
    
    
    piradip_axis_sample_buffer_out buffer( 
        .axilite(csr_if),
        .aximm(mem_if),
        .stream_out(stream_if),
        .trigger(trigger)
    );

endmodule
