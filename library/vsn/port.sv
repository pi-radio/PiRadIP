`timescale 1ns / 1ps

interface vsn_port #(
  parameter integer WIDTH=256
) (
  input logic clk,
  input logic resetn
);
  typedef logic [WIDTH-1:0] data_t;

  function data_width();
     data_width = WIDTH;
  endfunction // data_width

  logic aclk, aresetn;

  // This is 
  data_t a;
  data_t b;

  always_comb aclk = clk;
  always_comb aresetn = resetn;

  modport P(import data_width, input aclk, aresetn, a, output b);
endinterface // piradip_vsn_port

module vsn_port_connector(
  vsn_port.P A,
  vsn_port.P B,		    
);
  always_comb A.a = B.b;
  always_comb B.a = A.b;
endmodule


module vsn_addmul_zzz(
  input logic clk,
  input logic rst,
  input logic [15:0] a1,			       
  input logic [15:0] a2,
  input logic [17:0] b,
  input logic [47:0] c,
  output logic [47:0] result
);

  DSP48E2 #(
	    // Feature Control Attributes: Data Path Selection
	    .AMULTSEL("AD"),                    // Selects A input to multiplier (A, AD)
	    .A_INPUT("DIRECT"),                // Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
	    .BMULTSEL("B"),                    // Selects B input to multiplier (AD, B)
	    .B_INPUT("DIRECT"),                // Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
	    .PREADDINSEL("A"),                 // Selects input to pre-adder (A, B)
	    .RND(48'h000000000000),            // Rounding Constant
	    .USE_MULT("MULTIPLY"),             // Select multiplier usage (DYNAMIC, MULTIPLY, NONE)
	    .USE_SIMD("ONE48"),                // SIMD selection (FOUR12, ONE48, TWO24)
	    .USE_WIDEXOR("FALSE"),             // Use the Wide XOR function (FALSE, TRUE)
	    .XORSIMD("XOR24_48_96"),           // Mode of operation for the Wide XOR (XOR12, XOR24_48_96)
	    // Pattern Detector Attributes: Pattern Detection Configuration
	    .AUTORESET_PATDET("NO_RESET"),     // NO_RESET, RESET_MATCH, RESET_NOT_MATCH
	    .AUTORESET_PRIORITY("RESET"),      // Priority of AUTORESET vs. CEP (CEP, RESET).
	    .MASK(48'h3fffffffffff),           // 48-bit mask value for pattern detect (1=ignore)
	    .PATTERN(48'h000000000000),        // 48-bit pattern match for pattern detect
	    .SEL_MASK("MASK"),                 // C, MASK, ROUNDING_MODE1, ROUNDING_MODE2
	    .SEL_PATTERN("PATTERN"),           // Select pattern value (C, PATTERN)
	    .USE_PATTERN_DETECT("NO_PATDET"),  // Enable pattern detect (NO_PATDET, PATDET)
	    // Programmable Inversion Attributes: Specifies built-in programmable inversion on specific pins
	    .IS_ALUMODE_INVERTED(4'b0000),     // Optional inversion for ALUMODE
	    .IS_CARRYIN_INVERTED(1'b0),        // Optional inversion for CARRYIN
	    .IS_CLK_INVERTED(1'b0),            // Optional inversion for CLK
	    .IS_INMODE_INVERTED(5'b00000),     // Optional inversion for INMODE
	    .IS_OPMODE_INVERTED(9'b000000000), // Optional inversion for OPMODE
	    .IS_RSTALLCARRYIN_INVERTED(1'b0),  // Optional inversion for RSTALLCARRYIN
	    .IS_RSTALUMODE_INVERTED(1'b0),     // Optional inversion for RSTALUMODE
	    .IS_RSTA_INVERTED(1'b0),           // Optional inversion for RSTA
	    .IS_RSTB_INVERTED(1'b0),           // Optional inversion for RSTB
	    .IS_RSTCTRL_INVERTED(1'b0),        // Optional inversion for RSTCTRL
	    .IS_RSTC_INVERTED(1'b0),           // Optional inversion for RSTC
	    .IS_RSTD_INVERTED(1'b0),           // Optional inversion for RSTD
	    .IS_RSTINMODE_INVERTED(1'b0),      // Optional inversion for RSTINMODE
	    .IS_RSTM_INVERTED(1'b0),           // Optional inversion for RSTM
	    .IS_RSTP_INVERTED(1'b0),           // Optional inversion for RSTP
	    // Register Control Attributes: Pipeline Register Configuration
	    .ACASCREG(1),                      // Number of pipeline stages between A/ACIN and ACOUT (0-2)
	    .ADREG(1),                         // Pipeline stages for pre-adder (0-1)
	    .ALUMODEREG(1),                    // Pipeline stages for ALUMODE (0-1)
	    .AREG(1),                          // Pipeline stages for A (0-2)
	    .BCASCREG(1),                      // Number of pipeline stages between B/BCIN and BCOUT (0-2)
	    .BREG(1),                          // Pipeline stages for B (0-2)
	    .CARRYINREG(1),                    // Pipeline stages for CARRYIN (0-1)
	    .CARRYINSELREG(1),                 // Pipeline stages for CARRYINSEL (0-1)
	    .CREG(1),                          // Pipeline stages for C (0-1)
	    .DREG(1),                          // Pipeline stages for D (0-1)
	    .INMODEREG(1),                     // Pipeline stages for INMODE (0-1)
	    .MREG(1),                          // Multiplier pipeline stages (0-1)
	    .OPMODEREG(1),                     // Pipeline stages for OPMODE (0-1)
	    .PREG(1)                           // Number of pipeline stages for P (0-1)
	    )
  DSP48E2_inst (
		.CLK(clk),
		.RSTA(rst),
		.RSTALLCARRYIN(rst),
		.RSTALUMODE(rst),
		.RSTB(rst),
		.RSTC(rst),
		.RSTCTRL(rst),
		.RSTD(rst),
		.RSTINMODE(rst),
		.RSTM(rst),
		.RSTP(rst),

		// Add everything
		.ALUMODE(4'b0),

		
		.A({{14{a1[15]}}, a1}),
		.B(b),
		.C(c),
		.D({{11{a2[15]}}, a2}),

		.P(result),                           // 48-bit output: Primary data

		.CARRYIN(1'b0),                  // 1-bit input: Carry-in
		.CARRYINSEL(3'b0),               // 3-bit input: Carry select

		.INMODE(5'b10101),                 // 5-bit input: INMODE control
		.OPMODE(9'b000110101),                 // 9-bit input: Operation mode

		
		// Cascade outputs: Cascade Ports
		//.ACOUT(ACOUT),                   // 30-bit output: A port cascade
		//.BCOUT(BCOUT),                   // 18-bit output: B cascade
		//.CARRYCASCOUT(CARRYCASCOUT),     // 1-bit output: Cascade carry
		//.MULTSIGNOUT(MULTSIGNOUT),       // 1-bit output: Multiplier sign cascade
		//.PCOUT(PCOUT),                   // 48-bit output: Cascade output
		// Control outputs: Control Inputs/Status Bits
		//.OVERFLOW(OVERFLOW),             // 1-bit output: Overflow in add/acc
		//.PATTERNBDETECT(PATTERNBDETECT), // 1-bit output: Pattern bar detect
		//.PATTERNDETECT(PATTERNDETECT),   // 1-bit output: Pattern detect
		//.UNDERFLOW(UNDERFLOW),           // 1-bit output: Underflow in add/acc
		// Data outputs: Data Ports
		//.CARRYOUT(CARRYOUT),             // 4-bit output: Carry
		//.XOROUT(XOROUT),                 // 8-bit output: XOR data
		// Cascade inputs: Cascade Ports
		.ACIN(30'b0),                     // 30-bit input: A cascade data
		.BCIN(18'b0),                     // 18-bit input: B cascade
		.CARRYCASCIN(1'b0),       // 1-bit input: Cascade carry
		.MULTSIGNIN(1'b0),         // 1-bit input: Multiplier sign cascade
		.PCIN(48'b0),                     // 48-bit input: P cascade
		// Reset/Clock Enable inputs: Reset/Clock Enable Inputs
		.CEA1(1'b1),                     // 1-bit input: Clock enable for 1st stage AREG
		.CEA2(1'b1),                     // 1-bit input: Clock enable for 2nd stage AREG
		.CEAD(1'b1),                     // 1-bit input: Clock enable for ADREG
		.CEALUMODE(1'b1),                // 1-bit input: Clock enable for ALUMODE
		.CEB1(1'b1),                     // 1-bit input: Clock enable for 1st stage BREG
		.CEB2(1'b1),                     // 1-bit input: Clock enable for 2nd stage BREG
		.CEC(1'b1),                      // 1-bit input: Clock enable for CREG
		.CECARRYIN(1'b1),                // 1-bit input: Clock enable for CARRYINREG
		.CECTRL(1'b1),                   // 1-bit input: Clock enable for OPMODEREG and CARRYINSELREG
		.CED(1'b1),                      // 1-bit input: Clock enable for DREG
		.CEINMODE(1'b1),                 // 1-bit input: Clock enable for INMODEREG
		.CEM(1'b1),                      // 1-bit input: Clock enable for MREG
		.CEP(1'b1)                      // 1-bit input: Clock enable for PREG
		);  
  
endmodule


module vsn_sparam_3port #(
  parameter integer SAMPLE_WIDTH = 16,
  parameter integer NSAMPLES = 16
) (
  logic [NSAMPLES * SAMPLES_WIDTH-1:0] P0a,
  logic [NSAMPLES * SAMPLES_WIDTH-1:0] P0b,
  vsn_port.P P1,		    
  vsn_port.P P2
)

  logic [15:0] S00, S01, S02;
  logic [15:0] S10, S11, S12;
  logic [15:0] S20, S21, S22;

  // P0.b = S00 * P0.a + S01 * P1.a + S02 + P2.a
  // P1.b = S10 * P0.a + S11 * P1.a + S12 + P2.a
  // P2.b = S20 * P0.a + S21 * P1.a + S22 + P2.a

  
  
endmodule  




 
