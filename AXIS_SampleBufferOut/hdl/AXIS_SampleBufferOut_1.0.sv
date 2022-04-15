`timescale 1ns/1ps
module AXIS_SampleBufferOut #(
    parameter integer AXILITE_ADDR_WIDTH = 8,
    parameter integer AXILITE_DATA_WIDTH = 32,
    parameter integer AXIMM_ADDR_WIDTH = 32,
    parameter integer AXIMM_DATA_WIDTH = 32,
    parameter integer AXIMM_ID_WIDTH = 1,
    parameter integer AXIMM_AWUSER_WIDTH = 0,
    parameter integer AXIMM_ARUSER_WIDTH = 0,
    parameter integer AXIMM_WUSER_WIDTH = 0,
    parameter integer AXIMM_RUSER_WIDTH = 0,
    parameter integer AXIMM_BUSER_WIDTH = 0,
    parameter integer STREAM_OUT_WIDTH = 32,
    parameter integer STREAM_OUT_ID_WIDTH = 0,
    parameter integer STREAM_OUT_DEST_WIDTH = 0,
    parameter integer STREAM_OUT_USER_WIDTH = 0
) (
    logic,
    logic,
    logic,
    logic,
    logic[1:0],
    logic,
    logic,
    logic[AXILITE_DATA_WIDTH-1:0],
    logic[1:0],
    logic,
    logic[AXILITE_ADDR_WIDTH-1:0],
    logic[2:0],
    logic,
    logic[AXILITE_DATA_WIDTH-1:0],
    logic[AXILITE_DATA_WIDTH/8-1:0],
    logic,
    logic,
    logic[AXILITE_ADDR_WIDTH-1:0],
    logic[2:0],
    logic,
    logic,
    logic,
    logic,
    logic,
    logic,
    id_t,
    logic [1:0],
    buser_t,
    logic,
    logic,
    id_t,
    data_t,
    logic [1:0],
    logic,
    ruser_t,
    logic,
    id_t,
    addr_t,
    logic [7:0],
    logic [2:0],
    logic [1:0],
    logic,
    logic [3:0],
    logic [2:0],
    logic [3:0],
    logic [3:0],
    awuser_t,
    logic,
    data_t,
    strb_t,
    logic,
    wuser_t,
    logic,
    logic,
    id_t,
    addr_t,
    logic [7:0],
    logic [2:0],
    logic [1:0],
    logic,
    logic [3:0],
    logic [2:0],
    logic [3:0],
    logic [3:0],
    aruser_t,
    logic,
    logic,
    logic,
    logic,
    logic,
    logic,
    logic[STREAM_OUT_WIDTH-1:0],
    logic[BYTE_WIDTH-1:0],
    logic[BYTE_WIDTH-1:0],
    logic[STREAM_OUT_ID_WIDTH-1:0],
    logic[STREAM_OUT_DEST_WIDTH-1:0],
    logic[STREAM_OUT_USER_WIDTH-1:0],
    logic,
    None
);

    axi4mm_lite #(
        .ADDR_WIDTH(AXILITE_ADDR_WIDTH),
        .DATA_WIDTH(AXILITE_DATA_WIDTH)
    ) axi4mm_lite_inst (
        .clk(axilite_clk),
        .resetn(axilite_resetn)
    );
    assign axi4mm_lite_inst.awaddr = axilite_awaddr;
    assign axi4mm_lite_inst.awprot = axilite_awprot;
    assign axi4mm_lite_inst.awvalid = axilite_awvalid;
    assign axi4mm_lite_inst.wdata = axilite_wdata;
    assign axi4mm_lite_inst.wstrb = axilite_wstrb;
    assign axi4mm_lite_inst.wvalid = axilite_wvalid;
    assign axi4mm_lite_inst.bready = axilite_bready;
    assign axi4mm_lite_inst.araddr = axilite_araddr;
    assign axi4mm_lite_inst.arprot = axilite_arprot;
    assign axi4mm_lite_inst.arvalid = axilite_arvalid;
    assign axi4mm_lite_inst.rready = axilite_rready;
    assign axilite_awready = axi4mm_lite_inst.awready;
    assign axilite_wready = axi4mm_lite_inst.wready;
    assign axilite_bresp = axi4mm_lite_inst.bresp;
    assign axilite_bvalid = axi4mm_lite_inst.bvalid;
    assign axilite_arready = axi4mm_lite_inst.arready;
    assign axilite_rdata = axi4mm_lite_inst.rdata;
    assign axilite_rresp = axi4mm_lite_inst.rresp;
    assign axilite_rvalid = axi4mm_lite_inst.rvalid;

    axi4mm #(
        .ADDR_WIDTH(AXIMM_ADDR_WIDTH),
        .DATA_WIDTH(AXIMM_DATA_WIDTH),
        .ID_WIDTH(AXIMM_ID_WIDTH),
        .AWUSER_WIDTH(AXIMM_AWUSER_WIDTH),
        .ARUSER_WIDTH(AXIMM_ARUSER_WIDTH),
        .WUSER_WIDTH(AXIMM_WUSER_WIDTH),
        .RUSER_WIDTH(AXIMM_RUSER_WIDTH),
        .BUSER_WIDTH(AXIMM_BUSER_WIDTH)
    ) axi4mm_inst (
        .clk(aximm_clk),
        .resetn(aximm_resetn)
    );
    assign axi4mm_inst.awid = aximm_awid;
    assign axi4mm_inst.awaddr = aximm_awaddr;
    assign axi4mm_inst.awlen = aximm_awlen;
    assign axi4mm_inst.awsize = aximm_awsize;
    assign axi4mm_inst.awburst = aximm_awburst;
    assign axi4mm_inst.awlock = aximm_awlock;
    assign axi4mm_inst.awcache = aximm_awcache;
    assign axi4mm_inst.awprot = aximm_awprot;
    assign axi4mm_inst.awqos = aximm_awqos;
    assign axi4mm_inst.awregion = aximm_awregion;
    assign axi4mm_inst.awuser = aximm_awuser;
    assign axi4mm_inst.awvalid = aximm_awvalid;
    assign axi4mm_inst.wdata = aximm_wdata;
    assign axi4mm_inst.wstrb = aximm_wstrb;
    assign axi4mm_inst.wlast = aximm_wlast;
    assign axi4mm_inst.wuser = aximm_wuser;
    assign axi4mm_inst.wvalid = aximm_wvalid;
    assign axi4mm_inst.bready = aximm_bready;
    assign axi4mm_inst.arid = aximm_arid;
    assign axi4mm_inst.araddr = aximm_araddr;
    assign axi4mm_inst.arlen = aximm_arlen;
    assign axi4mm_inst.arsize = aximm_arsize;
    assign axi4mm_inst.arburst = aximm_arburst;
    assign axi4mm_inst.arlock = aximm_arlock;
    assign axi4mm_inst.arcache = aximm_arcache;
    assign axi4mm_inst.arprot = aximm_arprot;
    assign axi4mm_inst.arqos = aximm_arqos;
    assign axi4mm_inst.arregion = aximm_arregion;
    assign axi4mm_inst.aruser = aximm_aruser;
    assign axi4mm_inst.arvalid = aximm_arvalid;
    assign axi4mm_inst.rready = aximm_rready;
    assign aximm_awready = axi4mm_inst.awready;
    assign aximm_wready = axi4mm_inst.wready;
    assign aximm_bid = axi4mm_inst.bid;
    assign aximm_bresp = axi4mm_inst.bresp;
    assign aximm_buser = axi4mm_inst.buser;
    assign aximm_bvalid = axi4mm_inst.bvalid;
    assign aximm_arready = axi4mm_inst.arready;
    assign aximm_rid = axi4mm_inst.rid;
    assign aximm_rdata = axi4mm_inst.rdata;
    assign aximm_rresp = axi4mm_inst.rresp;
    assign aximm_rlast = axi4mm_inst.rlast;
    assign aximm_ruser = axi4mm_inst.ruser;
    assign aximm_rvalid = axi4mm_inst.rvalid;

    axi4s #(
        .WIDTH(STREAM_OUT_WIDTH),
        .ID_WIDTH(STREAM_OUT_ID_WIDTH),
        .DEST_WIDTH(STREAM_OUT_DEST_WIDTH),
        .USER_WIDTH(STREAM_OUT_USER_WIDTH)
    ) axi4s_inst (
        .clk(stream_out_clk),
        .resetn(stream_out_resetn)
    );
    assign axi4s_inst.tready = stream_out_tready;
    assign stream_out_tvalid = axi4s_inst.tvalid;
    assign stream_out_tlast = axi4s_inst.tlast;
    assign stream_out_tdata = axi4s_inst.tdata;
    assign stream_out_tstrb = axi4s_inst.tstrb;
    assign stream_out_tkeep = axi4s_inst.tkeep;
    assign stream_out_tid = axi4s_inst.tid;
    assign stream_out_tdest = axi4s_inst.tdest;
    assign stream_out_tuser = axi4s_inst.tuser;

    piradip_axis_sample_buffer_out #(
    ) piradip_axis_sample_buffer_out_inst (
        .axilite(axilite),
        .aximm(aximm),
        .stream_out(stream_out),
        .trigger(trigger)
    );
endmodule
