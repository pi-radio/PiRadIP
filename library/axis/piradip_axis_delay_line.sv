`timescale 1ns / 1ps

module piradip_axis_delay_line (
  axi4s.SUBORDINATE samples_in,
  axi4s.MANAGER samples_out,
  input logic [9:0] delay,
  input logic delay_clk,
  input logic delay_upd,
  input logic delay_upd
);
  localparam DEPTH_STREAM_WORDS = 1024;
  
  localparam DATA_WIDTH = samples_in.data_width();

  localparam MEMORY_BIT_WIDTH = $clog2(DATA_WIDTH * DEPTH_STREAM_WORDS);
  
  localparam ADDR_WIDTH = $clog2(DEPTH_STREAM_WORDS);

  logic [ADDR_WIDTH-1:0] delay_r, delay_so;
  
  logic [ADDR_WIDTH-1:0] write_addr;
  logic [ADDR_WIDTH-1:0] read_addr;

  localparam MEMORY_TYPE="auto";
  localparam READ_LATENCY_A = 1;
  localparam READ_LATENCY_B = 1;

  logic [1:0] ram_cnt;
  logic ram_ready;
  logic out_delay_upd;

  
  piradip_ram_if #(
      .DATA_WIDTH(DATA_WIDTH),
      .ADDR_WIDTH(ADDR_WIDTH)
  ) mem_in (
      .clk_in(samples_in.aclk),
      .rst_in(~samples_in.aresetn)
  );
  
  piradip_ram_if #(
      .DATA_WIDTH(DATA_WIDTH),
      .ADDR_WIDTH(ADDR_WIDTH)
  ) mem_out (
      .clk_in(samples_out.aclk),
      .rst_in(~samples_out.aresetn)
  );

  piradip_tdp_ram #(
      .MEMORY_SIZE(MEMORY_SIZE),
      .READ_LATENCY_A(READ_LATENCY_A),
      .READ_LATENCY_B(READ_LATENCY_B),
      .MEMORY_TYPE(MEMORY_TYPE)
  ) ram (
      .a(mem_in.RAM_PORT),
      .b(mem_out.RAM_PORT)
  );

  xpm_cdc_handshake #(
      .DEST_EXT_HSK(0),
      .DEST_SYNC_FF(4),
      .INIT_SYNC_FF(1),
      .SIM_ASSERT_CHK(1),
      .WIDTH(ADDR_WIDTH)
  ) cdc_in (
      .dest_clk(samples_in.aclk),
      .dest_out(delay_so),
      .dest_req(dst_req),

      .src_rcv (src_rcv),
      .src_clk (delay_clk),
      .src_in  (delay),
      .src_send(delay_upd)
  );
  
  xpm_cdc_pulse cdc_out (
    .dest_clk(samples_out.aclk),
    .dest_rst(samples_out.aresetn),
    .dest_pulse(out_delay_upd),
    .src_clk(delay_clk),
    .src_pulse(delay_upd),
    .src_rst(delay_rst)
  );

  always_comb mem_in.we = 1'b1;
  always_comb mem_in.en = 1'b1;
  always_comb mem_in.wdata = samples_in.tdata;
  
  
  always_comb mem_out.we = 1'b0;
  always_comb mem_out.en = 1'b1;
  always_comb samples_out.tdata = mem_out.rdata;
  
  always @(posedge samples_in.clk)
  begin
    if (~samples_in.resetn) begin
      mem_in.waddr <= 1;
    end else if (dst_req) begin
      mem_in.waddr <= delay;
    end else begin
      mem_in.waddr <= mem_in.waddr + 1;
    end
  end
  
  always @(posedge samples_out.clk)
  begin
    if (~samples_out.resetn) begin
      mem_out.raddr <= 0;
    end else if (out_delay_upd) begin
      mem_out.raddr <= 0;
    end else begin
      mem_out.raddr <= mem_out.raddr + 1;
    end
  end

endmodule
