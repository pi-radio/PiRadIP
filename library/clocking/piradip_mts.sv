`timescale 1ns / 1ps

module piradip_mts_clocking
  #(
    ) 
  (
  input logic resetn,
  input logic sysref_in,
  input logic pl_clk,
  output logic adc_clk,
  output logic dac_clk,
  output logic sysref_adc,
  output logic sysref_dac,
  output logic locked,
  output logic clk_in_stopped,
  output logic clk_fb_stopped
    );

  (* ASYNC_REG="true" *) logic r1;

  logic reset_high;

  logic sysref_pl;
  
  xpm_cdc_single #(
    .SRC_INPUT_REG(0),
    .DEST_SYNC_FF(2)
  ) pl_clk_sync (
    .dest_clk(pl_clk),
    .dest_out(sysref_pl),
    .src_clk(1'b0),
    .src_in(sysref_in)
  );

  xpm_cdc_single #(
    .SRC_INPUT_REG(0),
    .DEST_SYNC_FF(2)
  ) adc_clk_sync (
    .dest_clk(adc_clk),
    .dest_out(sysref_adc),
    .src_clk(1'b0),
    .src_in(sysref_pl)
  );

  xpm_cdc_single #(
    .SRC_INPUT_REG(0),
    .DEST_SYNC_FF(2)
  ) dac_clk_sync (
    .dest_clk(dac_clk),
    .dest_out(sysref_dac),
    .src_clk(1'b0),
    .src_in(sysref_pl)
  );
  
  
  always @(posedge pl_clk) r1 <= sysref_in;
  always @(posedge adc_clk) sysref_adc <= r1;
  always @(posedge dac_clk) sysref_dac <= r1;

  logic mmcm_clkfb_out, clkfboutb_unused;

  logic mmcm_clk_out0, mmcm_clk_out1;
  
  logic clkout0b_unused,
	clkout1b_unused,
	clkout2_unused, clkout2b_unused,
	clkout3_unused, clkout3b_unused,
	clkout4_unused,
	clkout5_unused,
	clkout6_unused;
  
  logic psdone_unused;
  logic cddcdone_unused;
  
  logic [6:0] daddr;
  logic [15:0] din;
  logic [15:0] dout;
  logic dclk, den, drdy, dwe;

  always_comb den = 1'b0;
  always_comb daddr = 7'b0;
  always_comb din = 16'b0;
  always_comb dwe = 1'b0;
  
  //always_comb locked = locked_int;

  BUFGCE clkout0_buf
   (.CE  (locked),
    .O   (adc_clk),
    .I   (mmcm_clk_out0));

  BUFGCE clkout1_buf
   (.CE  (locked),
    .O   (dac_clk),
    .I   (mmcm_clk_out1));
  
  MMCME4_ADV #(
    .BANDWIDTH            ("OPTIMIZED"),
    .CLKOUT4_CASCADE      ("FALSE"),
    .COMPENSATION         ("INTERNAL"),
    .STARTUP_WAIT         ("FALSE"),
    .DIVCLK_DIVIDE        (1),
    .CLKFBOUT_MULT_F      (10.0),
    .CLKFBOUT_PHASE       (0.000),
    .CLKFBOUT_USE_FINE_PS ("FALSE"),
    .CLKOUT0_DIVIDE_F     (2.0),
    .CLKOUT0_PHASE        (0.000),
    .CLKOUT0_DUTY_CYCLE   (0.500),
    .CLKOUT0_USE_FINE_PS  ("FALSE"),
    .CLKOUT1_DIVIDE       (4.0),
    .CLKOUT1_PHASE        (0.000),
    .CLKOUT1_DUTY_CYCLE   (0.500),
    .CLKOUT1_USE_FINE_PS  ("FALSE"),
    .CLKIN1_PERIOD        (9.765),
    .IS_RST_INVERTED      ("TRUE")
    ) mmce4 (
    // Input clocks
    // Tied to always select the primary input clock
    .CLKIN1              (pl_clk),
    .CLKIN2              (1'b0),
    .CLKINSEL            (1'b1),
    
    // Feedback
    .CLKFBOUT            (mmcm_clkfb_out),
    .CLKFBOUTB           (clkfboutb_unused),
    .CLKFBIN             (mmcm_clkfb_out),

    // Output clocks
    .CLKOUT0             (mmcm_clk_out0),
    .CLKOUT1             (mmcm_clk_out1),

    .CLKOUT0B            (clkout0b_unused),
    .CLKOUT1B            (clkout1b_unused),
    .CLKOUT2             (clkout2_unused),
    .CLKOUT2B            (clkout2b_unused),
    .CLKOUT3             (clkout3_unused),
    .CLKOUT3B            (clkout3b_unused),
    .CLKOUT4             (clkout4_unused),
    .CLKOUT5             (clkout5_unused),
    .CLKOUT6             (clkout6_unused),

    // Ports for dynamic reconfiguration
    .DADDR               (daddr),
    .DCLK                (dclk),
    .DEN                 (den),
    .DI                  (din),
    .DO                  (dout),
    .DRDY                (drdy),
    .DWE                 (dwe),

    .CDDCDONE            (cddcdone_unused),
    .CDDCREQ             (1'b0),
    
    // Ports for dynamic phase shift
    .PSCLK               (1'b0),
    .PSEN                (1'b0),
    .PSINCDEC            (1'b0),
    .PSDONE              (psdone_unused),
    
    // Other control and status signals
    .LOCKED              (locked),
    .CLKINSTOPPED        (clk_in_stopped),
    .CLKFBSTOPPED        (clk_fb_stopped),
    .PWRDWN              (1'b0),
    .RST                 (resetn)    
    );

 
  

endmodule
