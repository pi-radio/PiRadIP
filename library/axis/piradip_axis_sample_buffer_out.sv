`timescale 1ns / 1ps

module piradip_axis_sample_buffer_out (
    axi4mm_lite.SUBORDINATE axilite,
    axi4mm.SUBORDINATE aximm,
    axi4s.MANAGER stream_out,
    input trigger
);

  localparam AXIMM_DATA_WIDTH = aximm.data_width();
  localparam AXIMM_ADDR_WIDTH = aximm.addr_width();

  localparam MEMORY_BIT_WIDTH = AXIMM_ADDR_WIDTH + $clog2(AXIMM_DATA_WIDTH);

  localparam STREAM_DATA_WIDTH = stream_out.data_width();
  localparam STREAM_ADDR_WIDTH = MEMORY_BIT_WIDTH - $clog2(STREAM_DATA_WIDTH);

  localparam READ_LATENCY_A = 1;
  localparam READ_LATENCY_B = 1;

  logic stream_update;
  logic stream_stopped;
  logic stream_active;
  logic stream_one_shot;
  logic [STREAM_ADDR_WIDTH-1:0] stream_start_offset;
  logic [STREAM_ADDR_WIDTH-1:0] stream_end_offset;

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
      .STREAM_OFFSET_WIDTH(STREAM_ADDR_WIDTH)
  ) csr (
      .aximm(axilite),
      .stream_rstn(stream_out.aresetn),
      .stream_clk(stream_out.aclk),
      .*
  );


  piradip_tdp_ram ram (
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

  always @(posedge stream_out.aclk) begin
    if (~stream_out.aresetn) begin
      enable_stream  <= 1'b0;
      stream_stopped <= 1'b0;
    end else begin
      stream_stopped = 1'b0;

      if (stream_update) begin
        enable_stream <= stream_active;
      end else if ((mem_stream.addr >= stream_end_offset) && stream_one_shot) begin
        enable_stream <= 1'b0;
        stream_stopped = 1'b1;
      end else begin
        enable_stream <= enable_stream;
      end
    end
  end

  always @(posedge stream_out.aclk) begin
    if (~stream_out.aresetn) begin
      mem_stream.addr <= 0;
    end else begin
      if (stream_update & stream_active) begin
        mem_stream.addr <= stream_start_offset;
      end else if (enable_stream & gearbox_in.tready) begin
        mem_stream.addr <= (mem_stream.addr >= stream_end_offset) ? stream_start_offset : mem_stream.addr+1;
      end
    end
  end

  initial
    begin
      $display("Pi Radio Sample Buffer: %d %d %d",
	       AXIMM_DATA_WIDTH, AXIMM_ADDR_WIDTH,
	       MEMORY_BIT_WIDTH);
	       
    end				

endmodule
