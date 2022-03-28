`timescale 1ns / 1ps

module piradspi_top #(
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

    axi4mm_lite #(
        .ADDR_WIDTH(C_CSR_ADDR_WIDTH),
        .DATA_WIDTH(C_CSR_DATA_WIDTH)
    ) axilite ( 
        .clk(csr_aclk),
        .resetn(csr_aresetn)
    );
    
    /* Write Address Bus */
    assign axilite.awaddr = csr_awaddr;
    assign axilite.awprot = csr_awprot;
    assign axilite.awvalid = csr_awvalid;
    assign csr_awready = axilite.awready; 
    /* Write Data Bus */
    assign axilite.wdata = csr_wdata;
    assign axilite.wstrb = csr_wstrb;
    assign axilite.wvalid = csr_wvalid;
    assign csr_wready = axilite.wready;
    /* Write Response Bus */ 
    assign csr_bresp = axilite.bresp;
    assign csr_bvalid = axilite.bvalid;
    assign axilite.bready = csr_bready;
    /* Read Address Bus */ 
    assign axilite.araddr = csr_araddr;
    assign axilite.arprot = csr_arprot;
    assign axilite.arvalid = csr_arvalid;
    assign csr_arready = axilite.arready;
    /* Read Data Bus */
    assign csr_rdata = axilite.rdata;
    assign csr_rresp = axilite.rresp;
    assign csr_rvalid = axilite.rvalid;
    assign axilite.rready = csr_rready;  

    logic cmd_completed;
    logic engine_error;
    logic engine_busy;

    piradspi_csr # ( 
        .NUM_PROFILES(C_NUM_PROFILES),
        .DATA_WIDTH(C_CSR_DATA_WIDTH),
        .ADDR_WIDTH(C_CSR_ADDR_WIDTH)
    ) csr (
        .aximm(axilite.SUBORDINATE),
        .axis_cmd(cmd_stream.MANAGER),
        .axis_mosi(mosi_stream.MANAGER),
        .axis_miso(miso_stream.SUBORDINATE),
        .command_completed(cmd_completed),
        .intr_out(interrupt),
        .engine_error(engine_error),
        .engine_busy(engine_busy)
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
        .engine_error(engine_error),
        .engine_busy(engine_busy),
        .cmd_completed(cmd_completed)
    );
    
endmodule
