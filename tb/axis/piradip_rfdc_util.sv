`timescale 100ps / 1ps

module REAL_ADC (
  axi4s.MANAGER adc_out,
  output logic adc_clk,
  output logic axis_clk,
  output logic signed [15:0] cur_sample		 
);
  localparam DATA_WIDTH = adc_out.data_width();
  localparam SAMPLE_WIDTH = 16;
  localparam NSAMPLES = DATA_WIDTH / SAMPLE_WIDTH;
  
  logic signed [15:0] samples[$];

  logic [DATA_WIDTH-1:0] next_out;

  always #0.125ns adc_clk <= ~adc_clk;

  
  function automatic void add_sample(input logic signed[15:0] sample);
    samples.push_back(sample);
  endfunction

  task automatic drain();
    wait(samples.size() == 0);

    @(posedge adc_clk);
  endtask
  
  
  always_comb adc_out.tvalid = 1;

  always @(posedge adc_clk)
  begin
    if (samples.size() != 0) begin
      cur_sample <= samples.pop_front();
    end else begin
      cur_sample <= 0;
    end
  end

  always @(posedge adc_clk)
  begin
    next_out <= { cur_sample, next_out[DATA_WIDTH-1:SAMPLE_WIDTH] };
  end

  always @(posedge axis_clk)
  begin
    adc_out.tdata <= next_out;
  end
  
  initial
  begin

    integer i;
    adc_clk <= 1'b0;
    
    cur_sample <= 16'b0;
    next_out <= {DATA_WIDTH{1'b0}};
    adc_out.tdata <= {DATA_WIDTH{1'b0}};
    
    forever
    begin
      axis_clk <= 1'b1;
      repeat (SAMPLE_WIDTH/2) @(posedge adc_clk);
      axis_clk <= 1'b0;
      repeat (SAMPLE_WIDTH/2) @(posedge adc_clk);
    end	
  end
endmodule
   
module REAL_DAC (
  axi4s.SUBORDINATE dac_in,
  input dac_clk,
  input axis_clk,
  output logic signed [15:0] cur_sample		 
);

  
  localparam DATA_WIDTH = dac_in.data_width();
  localparam SAMPLE_WIDTH = 16;
  localparam NSAMPLES = DATA_WIDTH / SAMPLE_WIDTH;
  
  logic [DATA_WIDTH-1:0] sample_queue[$];

  always @(posedge dac_in.aclk)
  begin
    integer i;

    for (i = 0; i < NSAMPLES; i++) begin
      sample_queue.push_back(dac_in.tdata[i*SAMPLE_WIDTH+:SAMPLE_WIDTH]);
    end
  end   

  always_comb dac_in.tready = 1'b1;
  
  initial
  begin
    integer i;
    
    forever
    begin
      @(posedge dac_clk);
      
      if (sample_queue.size() >= NSAMPLES) begin
	cur_sample <= sample_queue.pop_front();

	repeat (NSAMPLES-1) @(posedge dac_clk) cur_sample <= sample_queue.pop_front();
      end else begin
	cur_sample <= 0;
	
	repeat (NSAMPLES-1) @(posedge dac_clk) cur_sample <= 0;
      end
    end	
  end

  
endmodule
