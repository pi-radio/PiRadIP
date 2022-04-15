`timescale 1ns/1ps
module piradspi_ip #(
    parameter integer CSR_ADDR_WIDTH = 8,
    parameter integer CSR_DATA_WIDTH = 32,
    parameter integer C_SPI_SEL_MODE = 1,
    parameter integer C_CSR_ADDR_WIDTH = 8,
    parameter integer C_SPI_SEL_WIDTH = 3,
    parameter integer C_NUM_PROFILES = 16
) (
    logic,
    logic,
    logic,
    logic,
    logic[1:0],
    logic,
    logic,
    logic[CSR_DATA_WIDTH-1:0],
    logic[1:0],
    logic,
    logic[CSR_ADDR_WIDTH-1:0],
    logic[2:0],
    logic,
    logic[CSR_DATA_WIDTH-1:0],
    logic[CSR_DATA_WIDTH/8-1:0],
    logic,
    logic,
    logic[CSR_ADDR_WIDTH-1:0],
    logic[2:0],
    logic,
    logic,
    None,
    None,
    None,
    None,
    None[C_SPI_SEL_WIDTH-1:0],
    None
);

    axi4mm_lite #(
        .ADDR_WIDTH(CSR_ADDR_WIDTH),
        .DATA_WIDTH(CSR_DATA_WIDTH)
    ) axi4mm_lite_inst (
        .clk(csr_clk),
        .resetn(csr_resetn)
    );
    assign axi4mm_lite_inst.awaddr = csr_awaddr;
    assign axi4mm_lite_inst.awprot = csr_awprot;
    assign axi4mm_lite_inst.awvalid = csr_awvalid;
    assign axi4mm_lite_inst.wdata = csr_wdata;
    assign axi4mm_lite_inst.wstrb = csr_wstrb;
    assign axi4mm_lite_inst.wvalid = csr_wvalid;
    assign axi4mm_lite_inst.bready = csr_bready;
    assign axi4mm_lite_inst.araddr = csr_araddr;
    assign axi4mm_lite_inst.arprot = csr_arprot;
    assign axi4mm_lite_inst.arvalid = csr_arvalid;
    assign axi4mm_lite_inst.rready = csr_rready;
    assign csr_awready = axi4mm_lite_inst.awready;
    assign csr_wready = axi4mm_lite_inst.wready;
    assign csr_bresp = axi4mm_lite_inst.bresp;
    assign csr_bvalid = axi4mm_lite_inst.bvalid;
    assign csr_arready = axi4mm_lite_inst.arready;
    assign csr_rdata = axi4mm_lite_inst.rdata;
    assign csr_rresp = axi4mm_lite_inst.rresp;
    assign csr_rvalid = axi4mm_lite_inst.rvalid;

    piradspi #(
    ) piradspi_inst (
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn_active(csn_active),
        .csn(csn),
        .interrupt(interrupt),
        .csr(csr)
    );
endmodule
