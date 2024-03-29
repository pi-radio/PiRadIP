`timescale 1ns / 1ps

module piradip_axis_sample_buffer_in #(
    parameter integer NWORDS=0,  // Number of 32-bit words
    parameter MEMORY_TYPE="auto"
) (
    axi4mm_lite.SUBORDINATE axilite,
    axi4mm.SUBORDINATE aximm,
    axi4s.SUBORDINATE stream_in,
    input trigger,
    output i_en,
    output q_en
);

  localparam AXIMM_DATA_WIDTH = aximm.data_width();
  localparam AXIMM_ADDR_WIDTH = aximm.addr_width();

  //  Memory size in bits
  localparam MEMORY_SIZE = (NWORDS == 0) ? (1 << (AXIMM_ADDR_WIDTH + 3)) : (NWORDS << 5); 
  
  localparam MEMORY_BIT_WIDTH = $clog2(MEMORY_SIZE);

  localparam STREAM_DATA_WIDTH = stream_in.data_width();
  localparam STREAM_ADDR_WIDTH = MEMORY_BIT_WIDTH - $clog2(STREAM_DATA_WIDTH);

  //assert((MEMORY_SIZE & ((1 << STREAM_DATA_WIDTH) - 1)) == 0)
  
  localparam READ_LATENCY_A = 1;
  localparam READ_LATENCY_B = 1;


  logic                         stream_update;
  logic                         stream_active;
  logic                         stream_one_shot;
  logic [STREAM_ADDR_WIDTH-1:0] stream_start_offset;
  logic [STREAM_ADDR_WIDTH-1:0] stream_end_offset;
  logic                         stream_wrap_toggle;
  
  logic                         enable_stream;
  logic                         stream_stopped;
  logic                         stream_write;
  
  piradip_ram_if #(
      .DATA_WIDTH(AXIMM_DATA_WIDTH),
      .ADDR_WIDTH(MEMORY_BIT_WIDTH - $clog2(AXIMM_DATA_WIDTH))
  ) mem_mm (
      .clk_in(aximm.aclk),
      .rst_in(~aximm.aresetn)
  );
  piradip_ram_if #(
      .DATA_WIDTH(STREAM_DATA_WIDTH),
      .ADDR_WIDTH(STREAM_ADDR_WIDTH)
  ) mem_stream (
      .clk_in(stream_in.aclk),
      .rst_in(~stream_in.aresetn)
  );

  piradip_axis_sample_buffer_csr #(
      .BUFFER_BYTES(MEMORY_SIZE / 8),
      .STREAM_DATA_WIDTH(STREAM_DATA_WIDTH),
      .STREAM_OFFSET_WIDTH(STREAM_ADDR_WIDTH)
  ) csr (
      .aximm(axilite),
      .stream_rstn(stream_in.aresetn),
      .stream_clk(stream_in.aclk),
      .*
  );

  piradip_tdp_ram #(
      .MEMORY_SIZE(MEMORY_SIZE),
      .READ_LATENCY_A(READ_LATENCY_A),
      .READ_LATENCY_B(READ_LATENCY_B),
      .MEMORY_TYPE(MEMORY_TYPE)
  ) ram (
      .a(mem_mm.RAM_PORT),
      .b(mem_stream.RAM_PORT)
  );

  assign mem_mm.en = 1'b1;
  assign mem_stream.en = 1'b1;

  piradip_axi4_ram_adapter #(
      .DATA_WIDTH(AXIMM_DATA_WIDTH),
      .ADDR_WIDTH(AXIMM_ADDR_WIDTH),
      .WE_WIDTH(1),
      .READ_LATENCY(READ_LATENCY_A)
  ) ram_adapter (
      .aximm(aximm),
      .mem  (mem_mm.CLIENT)
  );

  assign stream_write = stream_in.tready & stream_in.tvalid & enable_stream;

  assign stream_stopped = ~enable_stream;
  
  assign stream_in.tready = enable_stream;
  assign mem_stream.we = stream_write;
  assign mem_stream.wdata = stream_in.tdata;

  always @(posedge stream_in.aclk) begin
    if (~stream_in.aresetn) begin
      enable_stream  <= 1'b0;
    end else begin
      if (stream_update) begin
        enable_stream <= stream_active;
      end else if ((mem_stream.addr >= stream_end_offset) && stream_one_shot) begin
        enable_stream <= 1'b0;
      end else begin
        enable_stream <= enable_stream;
      end
    end
  end

  always @(posedge stream_in.aclk) begin
    if (~stream_in.aresetn) begin
      mem_stream.addr <= 0;
      stream_wrap_toggle <= 0;
    end else begin
      if (stream_update & stream_active) begin
        mem_stream.addr <= stream_start_offset;
      end else if (stream_write) begin
	if (mem_stream.addr >= stream_end_offset) begin
	  mem_stream.addr <= stream_start_offset;
	  stream_wrap_toggle <= ~stream_wrap_toggle;	  
	end else begin
	  mem_stream.addr <= mem_stream.addr + 1;
	end
      end
    end
  end


endmodule
