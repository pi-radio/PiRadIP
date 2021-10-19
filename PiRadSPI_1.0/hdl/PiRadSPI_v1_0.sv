
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
    parameter integer C_CSR_ADDR_WIDTH	= 4,
    parameter integer C_SPI_SEL_WIDTH   = 3
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
 
    typedef piradspi_types #(
        .REG_WIDTH(C_CSR_DATA_WIDTH)
    ) types_inst;
       
    wire [types_inst::CMD_FIFO_WIDTH-1:0] cmd_in_data, cmd_out_data;
    wire cmd_in_ready, cmd_in_valid, cmd_in_last;
    wire cmd_out_ready, cmd_out_valid, cmd_out_last;

    wire [types_inst::mosi_FIFO_WIDTH-1:0] mosi_in_data, mosi_out_data;
    wire mosi_in_ready, mosi_in_valid, mosi_in_last;
    wire mosi_out_ready, mosi_out_valid, mosi_out_last;

    wire [types_inst::miso_FIFO_WIDTH-1:0] miso_in_data, miso_out_data;
    wire miso_in_ready, miso_in_valid, miso_in_last;
    wire miso_out_ready, miso_out_valid, miso_out_last;


    piradspi_csr # ( 
        .C_S_AXI_DATA_WIDTH(C_CSR_DATA_WIDTH),
        .C_S_AXI_ADDR_WIDTH(C_CSR_ADDR_WIDTH)
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
        .s_axi_rready(csr_rready)
    );
    
    piradspi_engine #(
        .types(types_inst),
        .SEL_MODE(C_SPI_SEL_MODE),
        .SEL_WIDTH(C_SPI_SEL_WIDTH)
    ) engine (
        .clk(csr_aclk),
        .rstn(csr_aresetn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(csn),
        
        .cmd_valid(cmd_out_valid),
        .cmd_ready(cmd_out_ready),
        .cmd_data(cmd_out_data),
        .cmd_tlast(cmd_out_last),
        
        .mosi_valid(mosi_out_valid),
        .mosi_ready(mosi_out_ready),
        .mosi_data(mosi_out_data),
        .mosi_tlast(mosi_out_last),
        
        .miso_valid(miso_out_valid),
        .miso_ready(miso_out_ready),
        .miso_data(miso_out_data),
        .miso_tlast(miso_out_last)        
    );
    

    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::CMD_FIFO_WIDTH)
    ) cmd_fifo (
        .aclk(csr_aclk),
        .aresetn(csr_aresetn),
        .s_tdata(cmd_in_data),
        .s_tready(cmd_in_ready),
        .s_tvalid(cmd_in_valid),
        .s_tlast(cmd_in_last),
        .m_tdata(cmd_out_data),
        .m_tready(cmd_out_ready),
        .m_tvalid(cmd_out_valid),
        .m_tlast(cmd_out_last)
    );

    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::DATA_FIFO_WIDTH)
    ) mosi_fifo (
        .aclk(csr_aclk),
        .aresetn(csr_aresetn),
        .s_tdata(mosi_in_data),
        .s_tready(mosi_in_ready),
        .s_tvalid(mosi_in_valid),
        .s_tlast(mosi_in_last),
        .m_tdata(mosi_out_data),
        .m_tready(mosi_out_ready),
        .m_tvalid(mosi_out_valid),
        .m_tlast(mosi_out_last)
    );
    
    piradip_axis_fifo_sss #(
        .WIDTH(types_inst::DATA_FIFO_WIDTH)
    ) miso_fifo (
        .aclk(csr_aclk),
        .aresetn(csr_aresetn),
        .s_tdata(miso_in_data),
        .s_tready(miso_in_ready),
        .s_tvalid(miso_in_valid),
        .s_tlast(miso_in_last),
        .m_tdata(miso_out_data),
        .m_tready(miso_out_ready),
        .m_tvalid(miso_out_valid),
        .m_tlast(miso_out_last)
    );
endmodule
