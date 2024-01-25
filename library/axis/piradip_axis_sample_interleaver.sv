`timescale 1ns / 1ps

module piradip_axis_sample_interleaver (
   axi4s.SUBORDINATE I_in,
   axi4s.SUBORDINATE Q_in,
   axi4s.MANAGER IQ_out,
   input logic i_en,
   input logic q_en
);

  localparam SAMPLE_WIDTH=16;
  localparam I_WIDTH = I_in.data_width();
  localparam Q_WIDTH = Q_in.data_width();
  localparam OUT_WIDTH = IQ_out.data_width();
  
  localparam N_SAMPLES = OUT_WIDTH / SAMPLE_WIDTH;

  logic toggle;

  integer i;
  
  always_comb I_in.tready = IQ_out.tready;
  always_comb Q_in.tready = IQ_out.tready;
  
  always @(posedge IQ_out.aclk)
    begin
      if (~IQ_out.aresetn) begin
	IQ_out.tvalid <= 1'b0;
	IQ_out.tdata <= 0;
	toggle <= 0;
      end else if (i_en && q_en) begin
	toggle <= 0;

	IQ_out.tvalid <= I_in.tvalid & Q_in.tvalid;
	IQ_out.tstrb <= {(OUT_WIDTH/8){1'b1}};

	for (i = 0; i < N_SAMPLES/2; i++) begin
	  IQ_out.tdata[2*i*SAMPLE_WIDTH+:SAMPLE_WIDTH] <= I_in.tdata[i*SAMPLE_WIDTH+:SAMPLE_WIDTH];
	  IQ_out.tdata[(2*i+1)*SAMPLE_WIDTH+:SAMPLE_WIDTH] <= Q_in.tdata[i*SAMPLE_WIDTH+:SAMPLE_WIDTH];	 
	end
      end else if (!(i_en || q_en)) begin
	IQ_out.tdata <= 0;
	IQ_out.tstrb <= 0;
	IQ_out.tvalid <= 0;
      end else begin
	toggle <= ~toggle;


	IQ_out.tdata <= i_en ? I_in.tdata : Q_in.tdata;
	IQ_out.tstrb <= {(OUT_WIDTH/8){1'b1}};
	
	/*
	IQ_out.tvalid <= I_in.tvalid;
	
	if (!toggle) begin
	  IQ_out.tdata[I_WIDTH-1:0] <= i_en ? I_in.tdata : Q_in.tdata;
	  IQ_out.tdata[I_WIDTH+:I_WIDTH] <= 0;
	  IQ_out.tstrb <= { {(I_WIDTH/8){1'b0}}, {(I_WIDTH/8){1'b1}} };
	end else begin
	  IQ_out.tdata[I_WIDTH-1:0] <= 0;
	  IQ_out.tdata[I_WIDTH+:I_WIDTH] <= i_en ? I_in.tdata : Q_in.tdata;
	  IQ_out.tstrb <= { {(I_WIDTH/8){1'b1}}, {(I_WIDTH/8){1'b0}} };
	end
	*/
      end
    end // always @ (posedge IQ_out.aclk)
  
  initial
    begin
      assert(I_WIDTH == Q_WIDTH);
      assert(I_WIDTH + Q_WIDTH == OUT_WIDTH);
    end
endmodule
