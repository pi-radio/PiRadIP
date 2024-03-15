`timescale 1ns / 1ps

interface vsn_port #(
  parameter integer SAMPLE_WIDTH=16,
  parameter integer NSAMPLES=16
) (
);
  typedef logic [SAMPLE_WIDTH-1:0] sample_t;

  function integer data_width();
    return SAMPLE_WIDTH * NSAMPLES;
  endfunction // data_width

  function integer sample_width();
    return SAMPLE_WIDTH;
  endfunction // data_width

  function integer nsamples();
    return NSAMPLES;
  endfunction // data_width
  
  sample_t a[NSAMPLES];
  sample_t b[NSAMPLES];

  // U is the port for units, like S Parameter blocks
  // So the a port represents the forward wave into
  // the S parameter block, and b the reverse
  modport U(import data_width,
	    import sample_width,
	    import nsamples,
	    input a, 
	    output b);

  // V is the port looking from outside a unit, 
  // reversing the directions
  modport V(import data_width, 
	    input b, 
	    output a);

  initial
  begin
    $display("DATA_WIDTH: %d\n", SAMPLE_WIDTH * NSAMPLES);
  end
  
endinterface // piradip_vsn_port

module vsn_connection #(
  parameter integer SAMPLE_WIDTH=16,
  parameter integer NSAMPLES=16
)();
  vsn_port #(.SAMPLE_WIDTH(SAMPLE_WIDTH),
    .NSAMPLES(NSAMPLES)) P[2]();
  
  always_comb P[0].a = P[1].b;
  always_comb P[1].a = P[0].b;
endmodule








 
