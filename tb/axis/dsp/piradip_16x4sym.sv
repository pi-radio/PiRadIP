`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 03/28/2022 04:18:32 PM
// Design Name:
// Module Name: piradip_tb_sample_buffers
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////

module piradip_tb_16x4sym;
  localparam STREAM_WIDTH=256;
  
  logic mem_clk;
  logic mem_rstn;

  logic stream_clk;
  logic stream_rstn;

  logic adc_clk;

  logic signed [15:0] cur_adc_sample;
  logic signed [15:0] cur_dac_sample;

  
  piradip_tb_clkgen mm_clk_gen(.clk(mem_clk));
  
  axi4mm_lite ctrl(.clk(mem_clk), .resetn(mem_rstn));
  piradip_tb_axilite_manager control_manager(.aximm(ctrl));
  
  axi4s #(.WIDTH(256)) stream_in(.clk(stream_clk), .resetn(stream_rstn));
  axi4s #(.WIDTH(256)) stream_out(.clk(stream_clk), .resetn(stream_rstn));

  REAL_ADC adc(.adc_out(stream_in),
	       .adc_clk(adc_clk),
	       .axis_clk(stream_clk),
	       .cur_sample(cur_adc_sample));

  REAL_DAC dac(.dac_in(stream_out),
	       .dac_clk(adc_clk),
	       .axis_clk(stream_clk),
	       .cur_sample(cur_dac_sample));


  integer sample_queue[7];
  
  always @(posedge adc_clk)
  begin
    integer i;
    
    sample_queue[0] <= cur_adc_sample;

    for (i = 0; i < 6; i++) 
    begin
      sample_queue[i+1] <= sample_queue[i];
    end
  end // always @ (posedge adc_clk)
  

  integer signed r0, r1, r2, r3, computed_filter;

  integer signed rsum;
  
  always_comb
  begin
    r3 = 18'sh3f8ce * (sample_queue[0] + sample_queue[6]);
    r2 = 18'sh00d0f * (sample_queue[1] + sample_queue[5]);
    r1 = 18'sh3d798 * (sample_queue[2] + sample_queue[4]);
    r0 = 18'sh086ae * sample_queue[3];
    rsum = r1 + r2 + r3;
    computed_filter = (r0 + rsum) / 18'sh10000;
  end
  
  piradip_16x4sym filter(ctrl, stream_in, stream_out);

  logic [47:0] rr0, rr1, rr2, rr3, rrsum;

  localparam NZZQ = 3;
  
  integer signed zzq[NZZQ];

  always @(posedge adc_clk)
  begin
    integer i;

    zzq[0] <= sample_queue[3];
    
    for (i = 0; i < NZZQ-1; i++) 
    begin
      zzq[i+1] <= zzq[i];
    end    
  end

  
  piradip_addmul_zzz mul3(.clk(adc_clk),
			  .rst(~stream_rstn),
			  .a1(sample_queue[0]),			       
			  .a2(sample_queue[6]),
			  .b(18'sh3f8ce),
			  .c(48'd0),
			  .result(rr3));

  piradip_addmul_zzz mul2(.clk(adc_clk),
			  .rst(~stream_rstn),
			  .a1(sample_queue[1]),			       
			  .a2(sample_queue[5]),
			  .b(18'sh00d0f),
			  .c(48'd0),
			  .result(rr2));
  
  piradip_addmul_zzz mul1(.clk(adc_clk),
			  .rst(~stream_rstn),
			  .a1(sample_queue[2]),			       
			  .a2(sample_queue[4]),
			  .b(18'sh3d798),
			  .c(48'd0),
			  .result(rr1));

  always @(posedge adc_clk)
  begin
    rrsum <= rr1 + rr2 + rr3;
  end
  
  piradip_addmul_zzz mul0(.clk(adc_clk),
			  .rst(~stream_rstn),
			  .a1(zzq[NZZQ-1]),			       
			  .a2(16'b0),
			  .b(18'sh086ae),
			  .c(rrsum),
			  .result(rr0));
  
  logic signed [15:0] dsp48_filter_out;

  always_comb dsp48_filter_out = rr0[16+:16];

  
  logic done;
  integer i, j;
  integer ckpt;
  logic [255:0] d;

  localparam N_SAMPLES=16;
  localparam SAMPLE_WIDTH=16;
  localparam PI =  3.1415926535897;

  integer N;
  
  initial
    begin      
      mem_rstn <= 0;
      stream_rstn <= 0;      
      done <= 0;

      ckpt <= 0;
      
      mm_clk_gen.sleep(5);

      @(posedge stream_clk) stream_rstn <= 1;
      @(posedge mem_clk) mem_rstn <= 1;

      mm_clk_gen.sleep(20);

      for (i = 0; i < 10 * N_SAMPLES; i++) begin
	adc.add_sample(i);
      end

      adc.drain();
      mm_clk_gen.sleep(5);
      
      ckpt <= 1;      
	
      control_manager.write(4, 1);
      control_manager.sync();
		
      mm_clk_gen.sleep(5);

      for (i = 0; i < 10 * N_SAMPLES; i++) begin
	adc.add_sample(i);
      end

      adc.drain();
      mm_clk_gen.sleep(5);
	
      control_manager.write(4, 3);
      control_manager.sync();
		
      mm_clk_gen.sleep(5);

      for (i = 0; i < 10; i++) begin
	for (j = 0; j < N_SAMPLES; j++) begin
	  adc.add_sample((j == 0) ? 16'h8000 : 16'h0000);
	end
      end

      adc.drain();
      mm_clk_gen.sleep(20);
      
      ckpt <= 2;
      
      control_manager.write(8, 32'h086ae);
      control_manager.write(12, 32'h3d798);
      control_manager.write(16, 32'h00d0f);
      control_manager.write(20, 32'h3f8ce);

      control_manager.sync();

      ckpt <= 3;
      
      control_manager.write(4, 3);
      control_manager.sync();

      mm_clk_gen.sleep(5);      
      
      ckpt <= 4;


      for (i = 0; i < 16*32; i++) begin
	adc.add_sample(32767 * $sin(i * 2 * PI/16));
      end
		      
      ckpt <= 5;

      adc.drain();
      mm_clk_gen.sleep(20);


      for (i = 0; i < 16*32; i++) begin
	adc.add_sample(32767 * $sin(i * 2 * PI/19));
      end


      ckpt <= 6;

      adc.drain();
      mm_clk_gen.sleep(20);

      N = 64 * 1024;
      
      for (i = 0; i < N; i++) begin
	adc.add_sample(32767 * $sin(1000 * i * 2 * PI/N));
      end

		      
      ckpt <= 7;

      adc.drain();
      mm_clk_gen.sleep(20);

      
      $finish();
      
    end
  
endmodule;
