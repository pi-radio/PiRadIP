`timescale 1ns / 1ps

module piradspi #(
    parameter integer C_SPI_SEL_MODE   = 1,
    parameter integer C_CSR_ADDR_WIDTH = 8,
    parameter integer C_SPI_SEL_WIDTH  = 3,
    parameter integer C_NUM_PROFILES   = 16
) (
    input  logic io_clk,
    output logic sclk,
    output logic mosi,
    input  logic miso,

    output logic                       csn_active,
    output logic [C_SPI_SEL_WIDTH-1:0] csn,

    output logic interrupt,

    axi4mm_lite.SUBORDINATE csr
);

  import piradspi_pkg::*;

  localparam integer NSEL = C_SPI_SEL_MODE ? (1 << C_SPI_SEL_WIDTH) : (C_SPI_SEL_WIDTH);

  generate
    localparam integer DATA_FIFO_WIDTH = $bits(csr.wdata);

    axi4s #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) mosi_stream (
        .clk(csr.aclk),
        .resetn(csr.aresetn)
    );
    axi4s #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) miso_stream (
        .clk(csr.aclk),
        .resetn(csr.aresetn)
    );
  endgenerate

  logic cmd_completed;
  logic engine_error;
  logic engine_busy;

  piradspi_cmd_stream cmd_stream (
      .clk(csr.aclk),
      .resetn(csr.aresetn)
  );

  piradspi_csr #(
      .NUM_PROFILES(C_NUM_PROFILES)
  ) csr_inst (
      .csr(csr),
      .cmd_stream(cmd_stream.MANAGER),
      .axis_mosi(mosi_stream.MANAGER),
      .axis_miso(miso_stream.SUBORDINATE),
      .command_completed(cmd_completed),
      .intr_out(interrupt),
      .engine_error(engine_error),
      .engine_busy(engine_busy)
  );

  piradspi_fifo_engine #(
      .SEL_MODE (C_SPI_SEL_MODE),
      .SEL_WIDTH(C_SPI_SEL_WIDTH)
  ) engine (
      .io_clk(io_clk),
      .sclk(sclk),
      .mosi(mosi),
      .miso(miso),
      .sel_active(csn_active),
      .csn(csn),
      .cmd_stream(cmd_stream.SUBORDINATE),
      .axis_mosi(mosi_stream.SUBORDINATE),
      .axis_miso(miso_stream.MANAGER),
      .engine_error(engine_error),
      .engine_busy(engine_busy),
      .cmd_completed(cmd_completed)
  );

endmodule
