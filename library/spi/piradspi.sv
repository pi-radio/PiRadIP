`timescale 1ns / 1ps

module piradspi #(
    parameter integer C_SPI_SEL_MODE    = 1,
    parameter integer C_CSR_ADDR_WIDTH	= 8,
    parameter integer C_SPI_SEL_WIDTH   = 3,
    parameter integer C_NUM_PROFILES    = 16
) (
    output wire                             sclk,
    output wire                             mosi,
    input wire                              miso,
    
    output wire                             csn_active,
    output wire [C_SPI_SEL_WIDTH-1:0]       csn,

    output wire                             interrupt,

   axi4mm_lite.SUBORDINATE                  csr
);
    import piradspi::*;
    
    localparam integer NSEL            = C_SPI_SEL_MODE ? (1 << C_SPI_SEL_WIDTH) : (C_SPI_SEL_WIDTH);
    localparam DATA_FIFO_WIDTH         = $bits(csr.wdata);

    logic cmd_completed;
    logic engine_error;
    logic engine_busy;

    piradspi_csr # ( 
        .NUM_PROFILES(C_NUM_PROFILES),
        .DATA_WIDTH(C_CSR_DATA_WIDTH),
        .ADDR_WIDTH(C_CSR_ADDR_WIDTH)
    ) csr (
        .aximm(csr),
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
