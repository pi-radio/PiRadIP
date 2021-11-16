`timescale 1 ns / 1 ps

`include "piradspi.svh"
`include "piradip_axi4.svh"

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
    import piradspi::*;
    
    localparam integer NSEL            = C_SPI_SEL_MODE ? (1 << C_SPI_SEL_WIDTH) : (C_SPI_SEL_WIDTH);
    localparam DATA_FIFO_WIDTH         = C_CSR_DATA_WIDTH;

    `PIRADIP_AXI4LITE_SUBORDINATE_ADAPTER(axilite, C_CSR_, csr_);

    logic cmd_completed;

    piradspi_csr # ( 
        .NUM_PROFILES(C_NUM_PROFILES)
    ) csr (
        .aximm(axilite.SUBORDINATE),
        .axis_cmd(cmd_stream.MANAGER),
        .axis_mosi(mosi_stream.MANAGER),
        .axis_miso(miso_stream.SUBORDINATE),
        .command_completed(cmd_completed),
        .intr_out(interrupt)
    );
    
    axis_simple #(.WIDTH(CMD_FIFO_WIDTH)) cmd_stream(.clk(csr_aclk), .resetn(csr_aresetn));
    axis_simple #(.WIDTH(DATA_FIFO_WIDTH)) mosi_stream(.clk(csr_aclk), .resetn(csr_aresetn));
    axis_simple #(.WIDTH(DATA_FIFO_WIDTH)) miso_stream(.clk(csr_aclk), .resetn(csr_aresetn));    
    
    piradspi_fifo_engine #(
        .SEL_MODE(C_SPI_SEL_MODE),
        .SEL_WIDTH(C_SPI_SEL_WIDTH)
    ) engine (
        .clk(csr_aclk),
        .rstn(csr_aresetn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .sel_active(csn_active),
        .csn(csn),
        .axis_cmd(cmd_stream.SUBORDINATE),
        .axis_mosi(mosi_stream.SUBORDINATE),
        .axis_miso(miso_stream.MANAGER),
        .cmd_completed(cmd_completed)
    );
    
endmodule
