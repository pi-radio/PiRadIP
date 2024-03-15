module vsn_cdc #(
  parameter integer VSN_WIDTH=256
 ) (
  input logic clk_in,
  input logic rst,
  input logic [VSN_WIDTH-1:0] data_in,
  input logic clk_out,
  output logic [VSN_WIDTH-1:0] data_out
);		    
  
  logic wr_rst_busy, data_valid;

  logic [VSN_WIDTH-1:0] fifo_out;

  always_comb data_out = fifo_out; // data_valid ? fifo_out : 0;
  
  xpm_fifo_async #(
    .CASCADE_HEIGHT(0),        // DECIMAL
    .CDC_SYNC_STAGES(2),       // DECIMAL
    .DOUT_RESET_VALUE("0"),    // String
    .ECC_MODE("no_ecc"),       // String
    .FIFO_MEMORY_TYPE("auto"), // String
    .FIFO_READ_LATENCY(1),     // DECIMAL
    .FIFO_WRITE_DEPTH(16),   // DECIMAL
    .RD_DATA_COUNT_WIDTH(1),   // DECIMAL
    .READ_DATA_WIDTH(VSN_WIDTH),
    .READ_MODE("std"),         // String
    .RELATED_CLOCKS(0),        // DECIMAL
    .SIM_ASSERT_CHK(1),        // DECIMAL; 0=disable simulation messages, 1=enable simulation messages
    .USE_ADV_FEATURES("1000"), // String
    .WAKEUP_TIME(0),           // DECIMAL
    .WRITE_DATA_WIDTH(VSN_WIDTH),     // DECIMAL
    .WR_DATA_COUNT_WIDTH(1)    // DECIMAL
    )
  xpm_fifo_async_inst (
   .data_valid(),
   .dout(fifo_out),
   .din(data_in),
   .rd_clk(clk_out),
   .rd_en(1'b1),
   .rst(rst),
   .wr_clk(clk_in),
   .wr_rst_busy(wr_rst_busy),
   .wr_en(~rst & ~wr_rst_busy)                  // 1-bit input: Write Enable: If the FIFO is not full, asserting this
                                  // signal causes data (on din) to be written to the FIFO. Must be held
                                  // active-low when rst or wr_rst_busy is active high.

);
  
endmodule

module vsn_rfdc_adapter (
  axi4s.SUBORDINATE axis_a,
  axi4s.MANAGER axis_b,

  input logic vsn_clk,
  input logic vsn_rstn,
  vsn_port vsn
);

  localparam SAMPLE_WIDTH = vsn.sample_width();
  localparam NSAMPLES = vsn.nsamples();
  localparam VSN_WIDTH = vsn.data_width();

  $warning("SAMPLE_WIDTH: %d\n", SAMPLE_WIDTH);
  $warning("NSAMPLES: %d\n", NSAMPLES);
  $warning("VSN_WIDTH: %d\n", VSN_WIDTH);
  
  logic [VSN_WIDTH-1:0] vsn_a;
  logic [VSN_WIDTH-1:0] vsn_b;

  always_comb begin
    integer i;
    
    for (i = 0; i < NSAMPLES; i++)
    begin
      vsn_a[i * SAMPLE_WIDTH+:SAMPLE_WIDTH] = vsn.a[i];
      vsn.b[i] = vsn_b[i * SAMPLE_WIDTH+:SAMPLE_WIDTH];
    end
  end
  
  vsn_cdc #(
    .VSN_WIDTH(VSN_WIDTH)
    ) axis_to_vsn (
    .rst(~axis_a.aresetn),
    .clk_in(axis_a.aclk),
    .data_in(axis_a.tdata),
    .clk_out(vsn_clk),
    .data_out(vsn_b)
    );		    

  vsn_cdc #(
    .VSN_WIDTH(VSN_WIDTH)
    ) vsn_to_axis (
    .rst(~vsn_rstn),
    .clk_in(vsn_clk),
    .data_in(vsn_a),
    .clk_out(axis_b.aclk),
    .data_out(axis_b.tdata)
    );  
endmodule
