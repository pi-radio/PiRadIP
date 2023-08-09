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

module piradip_tb_sample_buffer_out
#(
    parameter MEMORY_ADDR_WIDTH = 10,
    parameter MEMORY_DATA_WIDTH = 32
 )
 (
  input logic mem_clk,
  input logic mem_rstn,
  input logic stream_clk,
  input logic stream_rstn,
  axi4s.MANAGER stream,
  output logic trigger
 );

  axi4mm_lite ctrl(.clk(mem_clk), .resetn(mem_rstn));
  axi4mm #(.ADDR_WIDTH(MEMORY_ADDR_WIDTH)) memory(.clk(mem_clk), .resetn(mem_rstn));
  
  piradip_tb_axilite_manager control_manager(.aximm(ctrl));
  piradip_tb_aximm_manager memory_manager(.aximm(memory));

  piradip_axis_sample_buffer_out sample_buffer (
						.axilite(ctrl.SUBORDINATE),
						.aximm(memory.SUBORDINATE),
						.stream_out(stream),
						.trigger(trigger)
						);

  integer i;
  
  initial
    begin
      trigger <= 1'b0;
      @(posedge mem_clk);
      while (~mem_rstn) @(posedge mem_clk);

      for (i = 0; i < (1 << (MEMORY_ADDR_WIDTH - 2)); i++) begin
        memory_manager.write_faf(4*i, { { i[5:0], 2'd3 },  { i[5:0], 2'd2 },  { i[5:0], 2'd1 },  { i[5:0], 2'd0 } });
      end

      memory_manager.sync();

      trigger <= 1'b1;
      @(posedge mem_clk);
      trigger <= 1'b0;
    end
  
endmodule


module piradip_tb_sample_buffer_in
#(
    parameter MEMORY_ADDR_WIDTH = 14,
    parameter MEMORY_DATA_WIDTH = 32
 )
 (
  input logic mem_clk,
  input logic mem_rstn,
  input logic stream_clk,
  input logic stream_rstn,
  axi4s.SUBORDINATE stream,
  input logic trigger,
  output logic done
 );
  axi4mm_lite ctrl(.clk(mem_clk), .resetn(mem_rstn));
  axi4mm #(.ADDR_WIDTH(MEMORY_ADDR_WIDTH)) memory(.clk(mem_clk), .resetn(mem_rstn));

  piradip_tb_axilite_manager control_manager(.aximm(ctrl.MANAGER));
  piradip_tb_aximm_manager memory_manager(.aximm(memory));

  piradip_axis_sample_buffer_in sample_buffer (
					       .axilite(ctrl.SUBORDINATE),
					       .aximm(memory.SUBORDINATE),
					       .stream_in(stream),
					       .trigger(trigger)
					       );


  class sbi_read_hander extends aximm_event_sink;
    virtual task read_done(input integer addr, input integer data, input integer resp);
      $display("Sample Buffer In: %08x: %08x %x", addr, data, resp);
    endtask
  endclass;
  
  sbi_read_hander read_handler = new();
  
  integer i;
  
  initial
    begin
      done <= 1'b0;
      @(posedge mem_clk);
      
      while(~mem_rstn) @(posedge mem_clk);

      repeat(5) @(posedge mem_clk);

      // Set to one shot
      control_manager.write(4, 2);
      
      while(~trigger) @(posedge mem_clk);

      $display("Received trigger");
      
      for (i = 0; i < 1000; i++)
	@(posedge mem_clk);
	  
      $display("Reading memory");
      
      for (i = 0; i < (1 << (MEMORY_ADDR_WIDTH - 2)); i++) begin
        memory_manager.read_async(4*i, read_handler);
      end

      for (i = 0; i < 5000; i++)
	@(posedge mem_clk);

      done <= 1'b1;
    end

endmodule

module piradip_tb_sample_buffers(
    );

  
  logic trigger;
  logic done;
  
  logic mem_clk;
  logic mem_rstn;

  logic stream_clk;
  logic stream_rstn;
  
  localparam MEMORY_ADDR_WIDTH = 14;
  localparam MEMORY_DATA_WIDTH = 32;
  localparam STREAM_WIDTH=128;
  
  piradip_tb_clkgen mm_clk_gen(.clk(mem_clk));
  piradip_tb_clkgen #(.HALF_PERIOD(1)) stream_clk_gen(.clk(stream_clk));
  
  axi4s #(.WIDTH(256)) stream(.clk(stream_clk), .resetn(stream_rstn));

  piradip_tb_sample_buffer_out sbo_tb(.stream(stream.MANAGER),
				      .*);
  
  piradip_tb_sample_buffer_in sbi_tb(.stream(stream.SUBORDINATE),
				     .*);
  
  integer i;
  
  initial
    begin
      mem_rstn <= 0;
      stream_rstn <= 0;      
      
      mm_clk_gen.sleep(5);
      
      @(posedge stream_clk) stream_rstn <= 1;
      @(posedge mem_clk) mem_rstn <= 1;

      while(~done) @(posedge mem_clk);
      





        $finish;
    end

endmodule
