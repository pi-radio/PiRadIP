`timescale 1ns / 1ps

module piradip_axis_sample_buffer_out #(
    parameter integer NWORDS=0,  // Number of 32-bit words
    parameter MEMORY_TYPE="auto",
    parameter USE_GEARBOX = 0
) (
    axi4mm_lite.SUBORDINATE axilite,
    axi4mm.SUBORDINATE aximm,
    axi4s.MANAGER stream_out,
    input trigger
);

  localparam AXIMM_DATA_WIDTH = aximm.data_width();
  localparam AXIMM_ADDR_WIDTH = aximm.addr_width();

  //  Memory size in bits
  localparam MEMORY_SIZE = (NWORDS == 0) ? (1 << (AXIMM_ADDR_WIDTH + 3)) : (NWORDS << 5); 
  localparam MEMORY_BIT_WIDTH = $clog2(MEMORY_SIZE);

  localparam STREAM_DATA_WIDTH = stream_out.data_width();
  localparam STREAM_ADDR_WIDTH = MEMORY_BIT_WIDTH - $clog2(STREAM_DATA_WIDTH);

  //assert ((MEMORY_SIZE & ((1 << STREAM_DATA_WIDTH) - 1)) == 0);
  
  localparam READ_LATENCY_A = 1;
  localparam READ_LATENCY_B = 1;

  logic stream_update;
  logic stream_stopped;
  logic stream_active;
  logic stream_one_shot;
  logic [STREAM_ADDR_WIDTH-1:0] stream_start_offset;
  logic [STREAM_ADDR_WIDTH-1:0] stream_end_offset;
  logic                         stream_wrap_toggle;

  logic i_en, q_en;
  
  logic enable_stream;

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
      .clk_in(stream_out.aclk),
      .rst_in(~stream_out.aresetn)
  );

  piradip_axis_sample_buffer_csr #(
      .BUFFER_BYTES(MEMORY_SIZE / 8),
      .STREAM_DATA_WIDTH(STREAM_DATA_WIDTH),
      .STREAM_OFFSET_WIDTH(STREAM_ADDR_WIDTH)
  ) csr (
      .aximm(axilite),
      .stream_rstn(stream_out.aresetn),
      .stream_clk(stream_out.aclk),
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

  assign mem_stream.we = 0;
  assign mem_stream.wdata = 0;

  logic out_ready;
  
  /*if (USE_GEARBOX != 0) begin
    axi4s #(
      .WIDTH(STREAM_DATA_WIDTH)
    ) gearbox_in (
      .clk(stream_out.aclk),
      .resetn(stream_out.aresetn)
    );

    piradip_axis_gearbox #(
      .DEPTH(16),
      .PROG_FULL_THRESH(5)
    ) gearbox (
      .in (gearbox_in.SUBORDINATE),
      .out(stream_out)
    );

    piradip_latency_synchronizer #(
      .OUT_OF_BAND_WIDTH(0),
      .IN_BAND_WIDTH(STREAM_DATA_WIDTH),
      .DATA_LATENCY(READ_LATENCY_B)
    ) stream_sync (
      .clk(stream_out.aclk),
      .resetn(stream_out.aresetn),
      .in_valid(enable_stream),
      .in_band(mem_stream.rdata),
      .out_valid(gearbox_in.tvalid),
      .out_data(gearbox_in.tdata)
    );
   
   always_comb out_ready = gearbox_in.tready;
  end else begin // if (USE_GEARBOX != 0)
  */
    piradip_latency_synchronizer #(
      .OUT_OF_BAND_WIDTH(0),
      .IN_BAND_WIDTH(STREAM_DATA_WIDTH),
      .DATA_LATENCY(READ_LATENCY_B)
    ) stream_sync (
      .clk(stream_out.aclk),
      .resetn(stream_out.aresetn),
      .in_valid(enable_stream),
      .in_band(mem_stream.rdata),
      .out_valid(stream_out.tvalid),
      .out_data(stream_out.tdata)
    );
  
   always_comb out_ready = stream_out.tready;
  //end  

  always_comb stream_stopped = ~enable_stream;

  always @(posedge stream_out.aclk) begin
    if (~stream_out.aresetn) begin
      enable_stream  <= 1'b0;
    end else if (stream_update) begin
      enable_stream  <= stream_active;
    end else if ((mem_stream.addr >= stream_end_offset) && stream_one_shot) begin
      enable_stream <= 1'b0;
    end else begin
      enable_stream <= enable_stream;
    end
  end

  always @(posedge stream_out.aclk) begin
    if (~stream_out.aresetn) begin
      mem_stream.addr <= 0;
      stream_wrap_toggle <= 0;
    end else begin
      if (stream_update & stream_active) begin
        mem_stream.addr <= stream_start_offset;
      end else if (enable_stream & out_ready) begin
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
