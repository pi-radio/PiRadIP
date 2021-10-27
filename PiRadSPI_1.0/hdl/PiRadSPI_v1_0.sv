
`timescale 1 ns / 1 ps

function integer piradspi_selwidth(input integer mode, input integer nsel);
    integer width, exp2;
    begin
        if (mode == 0) begin
            piradspi_selwidth = nsel;
        end else begin
            width=1;
            for (exp2 = 1; (exp2 << 1) <= nsel; exp2 = exp2 << 1) width = width + 1;
            piradspi_selwidth = width;
        end
    end
endfunction

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

    localparam integer NSEL            = C_SPI_SEL_MODE ? (1 << C_SPI_SEL_WIDTH) : (C_SPI_SEL_WIDTH);
       
    piradspi_csr # ( 
        .C_S_AXI_DATA_WIDTH(C_CSR_DATA_WIDTH),
        .C_S_AXI_ADDR_WIDTH(C_CSR_ADDR_WIDTH),
        .NUM_PROFILES(C_NUM_PROFILES)
    ) csr (
        .s_axi_aclk(csr_aclk),
        .s_axi_aresetn(csr_aresetn),
        .s_axi_awaddr(csr_awaddr),
        .s_axi_awprot(csr_awprot),
        .s_axi_awvalid(csr_awvalid),
        .s_axi_awready(csr_awready),
        .s_axi_wdata(csr_wdata),
        .s_axi_wstrb(csr_wstrb),
        .s_axi_wvalid(csr_wvalid),
        .s_axi_wready(csr_wready),
        .s_axi_bresp(csr_bresp),
        .s_axi_bvalid(csr_bvalid),
        .s_axi_bready(csr_bready),
        .s_axi_araddr(csr_araddr),
        .s_axi_arprot(csr_arprot),
        .s_axi_arvalid(csr_arvalid),
        .s_axi_arready(csr_arready),
        .s_axi_rdata(csr_rdata),
        .s_axi_rresp(csr_rresp),
        .s_axi_rvalid(csr_rvalid),
        .s_axi_rready(csr_rready),
        
        .axis_cmd(cmd_stream.MANAGER),
        .axis_mosi(mosi_stream.MANAGER),
        .axis_miso(miso_stream.SUBORDINATE)

    );
    
    axis_simple #(.WIDTH(engine.CMD_FIFO_WIDTH)) cmd_stream();
    axis_simple #(.WIDTH(engine.DATA_FIFO_WIDTH)) mosi_stream();
    axis_simple #(.WIDTH(engine.DATA_FIFO_WIDTH)) miso_stream();    
    
    piradspi_fifo_engine #(
        .SEL_MODE(C_SPI_SEL_MODE),
        .SEL_WIDTH(C_SPI_SEL_WIDTH)
    ) engine (
        .clk(csr_aclk),
        .rstn(csr_aresetn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(csn),
        .axis_cmd(cmd_stream.SUBORDINATE),
        .axis_mosi(mosi_stream.SUBORDINATE),
        .axis_miso(miso_stream.MANAGER),
        .cmd_completed(cmd_completed)
    );
    
endmodule
