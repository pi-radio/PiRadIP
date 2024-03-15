`timescale 1ns / 1ps

module piradip_tb_mts;

  logic sysref;
  logic plclk;
  logic resetn;

  logic sysref_adc, sysref_dac;

  logic adc_clk, dac_clk;

  logic locked;
  logic clk_in_stopped, clk_fb_stopped;
  
  always #50 sysref <= ~sysref;
  always #5 plclk <= ~plclk;

  piradip_mts_clocking mts(
    .resetn(resetn),
    .sysref_in(sysref),
    .pl_clk(plclk),
    .sysref_adc(sysref_adc),
    .sysref_dac(sysref_dac),
    .adc_clk(adc_clk),
    .dac_clk(dac_clk),
    .locked(locked),
    .clk_in_stopped(clk_in_stopped),
    .clk_fb_stopped(clk_fb_stopped)
  );
  
  initial
  begin
    sysref <= 1'b0;
    plclk <= 1'b0;
    resetn <= 1'b0;

    repeat(20) @(posedge plclk) resetn <= 1'b1;
  end
endmodule
