`timescale 1ns / 1ps

module piradip_axis_sample_interleaver (
   axi4s.SUBORDINATE I_in,
   axi4s.SUBORDINATE Q_in,
   axi4s.MANAGER IQ_out
);

  localparam SAMPLE_WIDTH=16;
  localparam I_WIDTH = I_in.data_width();
  localparam Q_WIDTH = Q_in.data_width();
  localparam OUT_WIDTH = IQ_out.data_width();
  
  localparam N_SAMPLES = I_WIDTH / SAMPLE_WIDTH / 2;
  
  genvar i;

  generate
    for (i = 0; i < N_SAMPLES; i++) 
      begin
	always_comb IQ_out.tdata[SAMPLE_WIDTH * (2 * i+1)+:SAMPLE_WIDTH] = I_in.tdata[SAMPLE_WIDTH * (2*i)+:SAMPLE_WIDTH];
	always_comb IQ_out.tdata[SAMPLE_WIDTH * (2 * i)+:SAMPLE_WIDTH] = Q_in.tdata[SAMPLE_WIDTH * (2*i+1)+:SAMPLE_WIDTH];
      end 
  endgenerate

  always_comb I_in.tready = IQ_out.tready;
  always_comb Q_in.tready = IQ_out.tready;
  always_comb IQ_out.tvalid = I_in.tvalid & Q_in.tvalid;

  initial
    begin
      assert(I_WIDTH == Q_WIDTH);
      assert(I_WIDTH == OUT_WIDTH);
    end
endmodule
