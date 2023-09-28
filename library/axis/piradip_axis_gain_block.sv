`timescale 1ns / 1ps

module piradip_simple_multiplier
  #(
    parameter A_WIDTH = 16,
    parameter B_WIDTH = 16,
    parameter OUT_WIDTH = 16,
    parameter FRACTIONAL_WIDTH = 8
    )
  (
   input logic clk,
   input logic rst,
   input logic [A_WIDTH-1:0] A,
   input logic [B_WIDTH-1:0] B,
   output logic [OUT_WIDTH-1:0] OUT
   );

  logic [29:0] Ain;
  logic [17:0] Bin;
  
  logic [47:0] P;

  generate
    if (A_WIDTH < 30) begin
      always_comb Ain = { {{30-A_WIDTH}{A[A_WIDTH-1]}}, A };
    end else begin
      always_comb Ain = A;
    end
  endgenerate

  generate
    if (B_WIDTH < 18) begin
      always_comb Bin = { {{18-B_WIDTH}{B[B_WIDTH-1]}}, B };
    end else begin
      always_comb Bin = B;
    end
  endgenerate
  
  always_comb
    OUT = P[FRACTIONAL_WIDTH+:OUT_WIDTH];
  
  DSP48E2 #(
		// Feature Control Attributes: Data Path Selection
		.AMULTSEL("A"),                    // Selects A input to multiplier (A, AD)
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

	        // Reset Inversion
		.IS_RSTALLCARRYIN_INVERTED(1'b1),  // Optional inversion for RSTALLCARRYIN
		.IS_RSTALUMODE_INVERTED(1'b1),     // Optional inversion for RSTALUMODE
		.IS_RSTA_INVERTED(1'b1),           // Optional inversion for RSTA
		.IS_RSTB_INVERTED(1'b1),           // Optional inversion for RSTB
		.IS_RSTCTRL_INVERTED(1'b1),        // Optional inversion for RSTCTRL
		.IS_RSTC_INVERTED(1'b1),           // Optional inversion for RSTC
		.IS_RSTD_INVERTED(1'b1),           // Optional inversion for RSTD
		.IS_RSTINMODE_INVERTED(1'b1),      // Optional inversion for RSTINMODE
		.IS_RSTM_INVERTED(1'b1),           // Optional inversion for RSTM
		.IS_RSTP_INVERTED(1'b1),           // Optional inversion for RSTP
	    
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

		    // Resets
		    .RSTA(rst),                     // 1-bit input: Reset for AREG
		    .RSTALLCARRYIN(rst),            // 1-bit input: Reset for CARRYINREG
		    .RSTALUMODE(rst),               // 1-bit input: Reset for ALUMODEREG
		    .RSTB(rst),                     // 1-bit input: Reset for BREG
		    .RSTC(rst),                     // 1-bit input: Reset for CREG
		    .RSTCTRL(rst),                  // 1-bit input: Reset for OPMODEREG and CARRYINSELREG
		    .RSTD(rst),                     // 1-bit input: Reset for DREG and ADREG
		    .RSTINMODE(rst),                // 1-bit input: Reset for INMODEREG
		    .RSTM(rst),                     // 1-bit input: Reset for MREG
		    .RSTP(rst),                     // 1-bit input: Reset for PREG
		    
		    
		    // Control registers
		    .ALUMODE(4'b0000),               // 4-bit input: ALU control
		    .OPMODE(9'b11_000_01_01),          // 9-bit input: Operation mode
		    .CARRYINSEL(3'b000),             // 3-bit input: Carry select
		    .INMODE(5'b00000),               // 5-bit input: INMODE control

		    // Data inputs: Data Ports
		    .A(Ain),                         // 30-bit input: A data
		    .B(Bin),                         // 18-bit input: B data
		    .C(48'b0),                       // 48-bit input: C data
		    .CARRYIN(1'b0),                  // 1-bit input: Carry-in
		    .D(27'b0),                       // 27-bit input: D data

		    // Data outputs: Data Ports
		    //.CARRYOUT(CARRYOUT),             // 4-bit output: Carry
		    .P(P),                           // 48-bit output: Primary data
		    //.XOROUT(XOROUT),                 // 8-bit output: XOR data

		    
		    // Cascade outputs: Cascade Ports
		    //.ACOUT(ACOUT),                   // 30-bit output: A port cascade
		    //.BCOUT(BCOUT),                   // 18-bit output: B cascade
		    //.CARRYCASCOUT(CARRYCASCOUT),     // 1-bit output: Cascade carry
		    //.MULTSIGNOUT(MULTSIGNOUT),       // 1-bit output: Multiplier sign cascade
		    //.PCOUT(PCOUT),                   // 48-bit output: Cascade output

		    // Control outputs: Control Inputs/Status Bits
		    .OVERFLOW(OVERFLOW),             // 1-bit output: Overflow in add/acc
		    .PATTERNBDETECT(PATTERNBDETECT), // 1-bit output: Pattern bar detect
		    .PATTERNDETECT(PATTERNDETECT),   // 1-bit output: Pattern detect
		    .UNDERFLOW(UNDERFLOW),           // 1-bit output: Underflow in add/acc


		    // Cascade inputs: Cascade Ports
		    .ACIN(30'b0),                     // 30-bit input: A cascade data
		    .BCIN(18'b0),                     // 18-bit input: B cascade
		    .CARRYCASCIN(1'b0),               // 1-bit input: Cascade carry
		    .MULTSIGNIN(1'b0),                // 1-bit input: Multiplier sign cascade
		    .PCIN(48'b0),                     // 48-bit input: P cascade

		    // Reset/Clock Enable inputs: Reset/Clock Enable Inputs
		    .CEA1(1'b0),                     // 1-bit input: Clock enable for 1st stage AREG
		    .CEA2(1'b1),                     // 1-bit input: Clock enable for 2nd stage AREG
		    .CEAD(1'b1),                     // 1-bit input: Clock enable for ADREG
		    .CEALUMODE(1'b1),                // 1-bit input: Clock enable for ALUMODE
		    .CEB1(1'b0),                     // 1-bit input: Clock enable for 1st stage BREG
		    .CEB2(1'b1),                     // 1-bit input: Clock enable for 2nd stage BREG
		    .CEC(1'b1),                      // 1-bit input: Clock enable for CREG
		    .CECARRYIN(1'b1),                // 1-bit input: Clock enable for CARRYINREG
		    .CECTRL(1'b1),                   // 1-bit input: Clock enable for OPMODEREG and CARRYINSELREG
		    .CED(1'b1),                      // 1-bit input: Clock enable for DREG
		    .CEINMODE(1'b1),                 // 1-bit input: Clock enable for INMODEREG
		    .CEM(1'b1),                      // 1-bit input: Clock enable for MREG
		    .CEP(1'b1)                       // 1-bit input: Clock enable for PREG
		    );

endmodule // piradip_axis_gain_block_multiplier



module piradip_axis_gain_block 
  #(
    parameter SAMPLE_WIDTH = 16,
    parameter FRACTIONAL_WIDTH = 8
    ) 
  (
   axi4mm_lite.SUBORDINATE axilite,
   axi4s.SUBORDINATE stream_in,
   axi4s.MANAGER stream_out
   );
  
  localparam DATA_WIDTH = axilite.data_width();
  localparam ADDR_WIDTH = axilite.addr_width();
  localparam REGISTER_ADDR_BITS = ADDR_WIDTH - $clog2(DATA_WIDTH / 8);

  localparam STREAM_DATA_WIDTH = stream_in.data_width();

  localparam NSAMPLES = STREAM_DATA_WIDTH / SAMPLE_WIDTH;

  localparam REGISTER_ID = 0;
  localparam REGISTER_GAIN = 1;  

  localparam MULT_LATENCY = 3;
  
  genvar i;

  logic [17:0] gain;

  logic [4:0] cnt;

  logic [STREAM_DATA_WIDTH-1:0] result;

  piradip_latency_synchronizer #(
      .OUT_OF_BAND_WIDTH(1),
      .IN_BAND_WIDTH(STREAM_DATA_WIDTH),
      .DATA_LATENCY(MULT_LATENCY)
  ) stream_sync (
      .clk(stream_out.aclk),
      .resetn(stream_out.aresetn),
      .in_valid(stream_in.tvalid & stream_in.tready),
      .in_band(result),
      .out_of_band(stream_in.tlast),
      .out_valid(stream_out.tvalid),
      .out_data({ stream_out.tlast, stream_out.tdata })
  );

  
  always @(posedge stream_in.aclk) begin
    if (!stream_in.aresetn) begin
      cnt <= 31;
    end else if (cnt) begin
      cnt <= cnt - 1;
    end
  end
    
  always_comb stream_in.tready <= (cnt == 0) & stream_out.tready;
  
  generate
    for (i = 0; i < NSAMPLES; i++) begin
      piradip_simple_multiplier #(
        .A_WIDTH(SAMPLE_WIDTH),
	.B_WIDTH(18),
	.FRACTIONAL_WIDTH(FRACTIONAL_WIDTH),
	.OUT_WIDTH(SAMPLE_WIDTH)
      ) mult (
	.clk(stream_in.aclk),
	.rst(stream_in.aresetn),
	.A(stream_in.tdata[SAMPLE_WIDTH*i+:SAMPLE_WIDTH]),
	.B(gain),
	.OUT(result[SAMPLE_WIDTH*i+:SAMPLE_WIDTH])
      );
    end
  endgenerate


  piradip_register_if #(
      .DATA_WIDTH(DATA_WIDTH),
      .REGISTER_ADDR_BITS(REGISTER_ADDR_BITS)
  ) reg_if (
      .aclk(axilite.aclk),
      .aresetn(axilite.aresetn)
  );
  
  piradip_axi4mmlite_subordinate sub_imp (
      .reg_if(reg_if.SERVER),
      .aximm (axilite),
      .*
  );

  always @(posedge axilite.aclk) begin
    if (~axilite.aresetn) begin
      gain <= 1 << FRACTIONAL_WIDTH;
    end else begin
      if (reg_if.wren) begin
        case (reg_if.wreg_no)
	  REGISTER_GAIN: begin
	    gain <= reg_if.wreg_data;
	  end
        endcase
      end // if (reg_if.wren)
    end
  end // always @ (posedge aximm.aclk)

  always_comb begin
    case (reg_if.rreg_no)
      REGISTER_ID: begin
	reg_if.rreg_data = 32'h50534742;
      end
      REGISTER_GAIN: begin
	reg_if.rreg_data = gain;
      end
    endcase
  end

  
endmodule
