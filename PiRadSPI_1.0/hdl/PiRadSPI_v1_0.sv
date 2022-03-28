`timescale 1 ns / 1 ps

module PiRadSPI_v1_0 #(
    parameter integer C_SPI_SEL_MODE    = 1,
    parameter integer C_CSR_DATA_WIDTH	= 32,
    parameter integer C_CSR_ADDR_WIDTH	= 8,
    parameter integer C_SPI_SEL_WIDTH   = 3,
    parameter integer C_NUM_PROFILES    = 16
) (
    output wire sclk,
    output wire mosi,
    input wire miso,
    
    output wire csn_active,
    output wire [C_SPI_SEL_WIDTH-1:0] csn,

    output wire interrupt,

    input wire  csr_aclk,
    input wire  csr_aresetn,
    input wire [C_CSR_ADDR_WIDTH-1 : 0] csr_awaddr,
    input wire [2 : 0] csr_awprot,
    input wire  csr_awvalid,
    output wire  csr_awready,
    input wire [C_CSR_DATA_WIDTH-1 : 0] csr_wdata,
    input wire [(C_CSR_DATA_WIDTH/8)-1 : 0] csr_wstrb,
    input wire  csr_wvalid,
    output wire  csr_wready,
    output wire [1 : 0] csr_bresp,
    output wire  csr_bvalid,
    input wire  csr_bready,
    input wire [C_CSR_ADDR_WIDTH-1 : 0] csr_araddr,
    input wire [2 : 0] csr_arprot,
    input wire  csr_arvalid,
    output wire  csr_arready,
    output wire [C_CSR_DATA_WIDTH-1 : 0] csr_rdata,
    output wire [1 : 0] csr_rresp,
    output wire  csr_rvalid,
    input wire  csr_rready
);
    piradspi_top #(
        .C_SPI_SEL_MODE(C_SPI_SEL_MODE),
        .C_CSR_DATA_WIDTH(C_CSR_DATA_WIDTH),
        .C_CSR_ADDR_WIDTH(C_CSR_ADDR_WIDTH),
        .C_SPI_SEL_WIDTH(C_SPI_SEL_WIDTH),
        .C_NUM_PROFILES(C_NUM_PROFILES)
    ) spi_top ( .* );
endmodule
