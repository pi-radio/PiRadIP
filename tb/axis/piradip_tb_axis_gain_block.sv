`timescale 1ns / 1ps

module piradip_tb_axis_gain_block(
    );
  logic done;
  
  logic mem_clk;
  logic mem_rstn;

  logic stream_clk;
  logic stream_rstn;
  
  localparam MEMORY_ADDR_WIDTH = 14;
  localparam MEMORY_DATA_WIDTH = 32;

  localparam SAMPLE_WIDTH=16;
  localparam N_SAMPLES=8;
  localparam STREAM_WIDTH=N_SAMPLES * SAMPLE_WIDTH;
  
  piradip_tb_clkgen mm_clk_gen(.clk(mem_clk));
  piradip_tb_clkgen #(.HALF_PERIOD(1)) stream_clk_gen(.clk(stream_clk));

  axi4mm_lite reg_bus(.clk(mem_clk), .resetn(mem_rstn));
  
  axi4s #(.WIDTH(STREAM_WIDTH)) samples_in(.clk(stream_clk), .resetn(stream_rstn));
  axi4s #(.WIDTH(STREAM_WIDTH)) samples_out(.clk(stream_clk), .resetn(stream_rstn));

  piradip_util_axi4s_manager samples_in_mgr(.name("Samples In"), .manager_out(samples_in));
  piradip_util_axi4s_subordinate samples_out_sub(.name("Samples In"), .sub_in(samples_out));

  piradip_axis_gain_block #(
    .SAMPLE_WIDTH(SAMPLE_WIDTH),
    .FRACTIONAL_WIDTH(8)		    
  ) gain_block (
    .axilite(reg_bus),
    .stream_in(samples_in),
    .stream_out(samples_out)		
  );

  integer i, j;
  logic [STREAM_WIDTH-1:0] d;
  
  initial
    begin
      mem_rstn <= 0;
      stream_rstn <= 0;      
      done <= 0;
      
      mm_clk_gen.sleep(5);

      samples_out_sub.ready();
      
      @(posedge stream_clk) stream_rstn <= 1;
      @(posedge mem_clk) mem_rstn <= 1;

      for (i = 0; i < 100; i++) begin
	for (j = 0; j < N_SAMPLES; j++) begin
	  d[j * SAMPLE_WIDTH+:SAMPLE_WIDTH] = i * N_SAMPLES + j;
	end

	samples_in_mgr.send_one(d, (i & 7) == 0);
      end
			       

      
      //while(~done) @(posedge mem_clk);

      for (i = 0; i < 1000; i++) @(posedge mem_clk);
      




      $finish;
    end
  
  
endmodule  
