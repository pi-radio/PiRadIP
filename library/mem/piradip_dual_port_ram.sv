`timescale 1ns / 1ps

interface piradip_ram_if #(
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 10
) (
    input logic clk_in,
    input logic rst_in
);

  logic clk;
  logic rst;
  logic en;
  logic we;
  logic [ADDR_WIDTH-1:0] addr;
  logic [DATA_WIDTH-1:0] wdata;
  logic [DATA_WIDTH-1:0] rdata;

  assign clk = clk_in;
  assign rst = rst_in;

  function integer data_width();
    return DATA_WIDTH;
  endfunction

  function integer addr_width();
    return ADDR_WIDTH;
  endfunction

  function integer memory_size();
    return DATA_WIDTH << ADDR_WIDTH;
  endfunction

  modport CLIENT(import data_width, import addr_width, import memory_size,
		 input clk, rst, rdata, output en, we, addr, wdata);

  modport RAM_PORT(import data_width, import addr_width, import memory_size,
		   input clk, rst, en, we, addr, wdata, output rdata);

endinterface

module piradip_tdp_ram #(
    parameter integer MEMORY_SIZE = 0,
    parameter integer READ_LATENCY_A = 1,
    parameter integer READ_LATENCY_B = 1,
    parameter integer READ_RESET_VALUE_A = 0,
    parameter integer READ_RESET_VALUE_B = 0,
    parameter MEMORY_TYPE = "auto"
) (
    piradip_ram_if.RAM_PORT a,
    piradip_ram_if.RAM_PORT b
);

  localparam A_ADDR_WIDTH = a.addr_width();
  localparam A_DATA_WIDTH = a.data_width();

  localparam B_ADDR_WIDTH = b.addr_width();
  localparam B_DATA_WIDTH = b.data_width();

  localparam MEMORY_BITS = (MEMORY_SIZE == 0) ? a.memory_size() : MEMORY_SIZE;

  generate
    if (a.memory_size() != b.memory_size())
      $error(
          "A and B iterfaces have different memory sizes (A: 2^%d %d bit words (%d bits) B: 2^%d %d bit words (%d bits))",
          A_ADDR_WIDTH,
          A_DATA_WIDTH,
          A_DATA_WIDTH << A_ADDR_WIDTH,
          B_ADDR_WIDTH,
          B_DATA_WIDTH,
          B_DATA_WIDTH << B_ADDR_WIDTH
      );
  endgenerate

  xpm_memory_tdpram #(
      .ADDR_WIDTH_A(A_ADDR_WIDTH),
      .BYTE_WRITE_WIDTH_A(A_DATA_WIDTH),
      .READ_DATA_WIDTH_A(A_DATA_WIDTH),
      .READ_LATENCY_A(READ_LATENCY_A),
      .READ_RESET_VALUE_A(READ_RESET_VALUE_A),
      .RST_MODE_A("SYNC"),
      .WRITE_DATA_WIDTH_A(A_DATA_WIDTH),
      .WRITE_MODE_A("no_change"),

      .ADDR_WIDTH_B(B_ADDR_WIDTH),
      .BYTE_WRITE_WIDTH_B(B_DATA_WIDTH),
      .READ_DATA_WIDTH_B(B_DATA_WIDTH),
      .READ_LATENCY_B(READ_LATENCY_B),
      .READ_RESET_VALUE_B(READ_RESET_VALUE_B),
      .RST_MODE_B("SYNC"),
      .WRITE_DATA_WIDTH_B(B_DATA_WIDTH),
      .WRITE_MODE_B("no_change"),

      .CASCADE_HEIGHT(0),
      .CLOCKING_MODE("independent_clock"),
      .ECC_MODE("no_ecc"),
      .MEMORY_INIT_FILE("none"),
      .MEMORY_INIT_PARAM("0"),
      .MEMORY_OPTIMIZATION("true"),
      .MEMORY_PRIMITIVE(MEMORY_TYPE),
      .MEMORY_SIZE(MEMORY_BITS),
      .MESSAGE_CONTROL(0),
      .SIM_ASSERT_CHK(1),
      .WAKEUP_TIME("disable_sleep")
  ) ram (
      .sleep(1'b0),

      .clka(a.clk),
      .rsta(a.rst),
      .ena(a.en),
      .wea(a.we),
      .addra(a.addr),
      .dina(a.wdata),
      .douta(a.rdata),
      .regcea(1'b1),

      .clkb(b.clk),
      .rstb(b.rst),
      .enb(b.en),
      .web(b.we),
      .addrb(b.addr),
      .dinb(b.wdata),
      .doutb(b.rdata),
      .regceb(1'b1)
  );

endmodule
