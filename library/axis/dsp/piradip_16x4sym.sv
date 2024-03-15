`timescale 1ns / 1ps

module piradip_addmul_zzz(
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

package piradip_fir;
  localparam REGISTER_ID = 0;
  localparam REGISTER_CTRLSTAT = 1;

  localparam CTRLSTAT_ACTIVE = 0;
  localparam CTRLSTAT_UPDATE = 1;

  localparam REGISTER_COEF_BASE = 2;
endpackage

module piradip_fir_csr #(
    NCOEF = 4,
    COEF_WIDTH = 18
) (
    axi4mm_lite.SUBORDINATE aximm,

    input logic stream_rstn,
    input logic stream_clk,
    output logic stream_update,
    output logic stream_active,
    output logic [NCOEF * COEF_WIDTH-1:0] stream_coef
);
  localparam DATA_WIDTH = aximm.data_width();
  localparam ADDR_WIDTH = aximm.addr_width();
  localparam REGISTER_ADDR_BITS = ADDR_WIDTH - $clog2(DATA_WIDTH / 8);

  import piradip_fir::*;

  logic ctrl_stat_write;
  logic initialized;

  logic                           mm_req_update;
  logic                           mm_active;
  logic                           mm_update;
  logic [NCOEF * COEF_WIDTH-1:0]  mm_coef;

  logic [COEF_WIDTH-1:0] mm_coef_array[NCOEF];
  
  localparam CDC_WIDTH = 1 + COEF_WIDTH * NCOEF;
  
  piradip_register_if #(
      .DATA_WIDTH(DATA_WIDTH),
      .REGISTER_ADDR_BITS(REGISTER_ADDR_BITS)
  ) reg_if (
      .aclk(aximm.aclk),
      .aresetn(aximm.aresetn)
  );

  piradip_axi4mmlite_subordinate sub_imp (
      .reg_if(reg_if.SERVER),
      .aximm (aximm),
      .*
  );

  piradip_cdc_auto_word #(
      .WIDTH(CDC_WIDTH)
  ) ctrl_cdc (
      .src_rst(~aximm.aresetn),
      .src_clk(aximm.aclk),
      .src_data({ mm_active, mm_coef }),
      .src_send(mm_update),
      .dst_rst(~stream_rstn),
      .dst_clk(stream_clk),
      .dst_data({ stream_active, stream_coef }),
      .dst_update(stream_update)
  );

  always_comb mm_req_update = ((reg_if.wreg_no == REGISTER_CTRLSTAT && reg_if.wreg_data[CTRLSTAT_UPDATE]) ||
			       (reg_if.wreg_no == REGISTER_CTRLSTAT && reg_if.wreg_data[CTRLSTAT_ACTIVE] != mm_active));
  
  always @(posedge aximm.aclk) begin
    initialized <= ~aximm.aresetn ? 1'b0 : (initialized | mm_update);
    mm_update <= aximm.aresetn && ((reg_if.wren && mm_req_update) | ~initialized);
  end

  
  always_comb begin
    integer i;
    
    for (i = 0; i < NCOEF; i++) begin
      mm_coef[COEF_WIDTH * i+:COEF_WIDTH] = mm_coef_array[i];
    end
  end
  
  always @(posedge aximm.aclk) begin
    integer i;
	
    if (~aximm.aresetn) begin
      mm_active <= 0;

      mm_coef_array[0] = 18'h10000;
      
      for (i = 1; i < NCOEF; i++) begin
	mm_coef_array[i] = 18'h0;
      end
    end else begin
      if (reg_if.wren) begin
	if (reg_if.wreg_no >= REGISTER_COEF_BASE && 
	    reg_if.wreg_no < REGISTER_COEF_BASE + NCOEF) begin
	  mm_coef_array[reg_if.wreg_no - REGISTER_COEF_BASE] <= reg_if.wreg_data;
	end else if (reg_if.wreg_no == REGISTER_CTRLSTAT) begin
	  mm_active <= reg_if.wreg_data[CTRLSTAT_ACTIVE];
	end	
      end // if (reg_if.wren)
    end
  end // always @ (posedge aximm.aclk)

  always_comb begin
    if (reg_if.rreg_no == REGISTER_ID) begin
      reg_if.rreg_data = 32'h46495237;
    end else if (reg_if.rreg_no == REGISTER_CTRLSTAT) begin
      reg_if.rreg_data = { 31'b0, mm_active };
    end else if (reg_if.rreg_no >= REGISTER_COEF_BASE && 
		 reg_if.rreg_no < REGISTER_COEF_BASE + NCOEF) begin
      reg_if.rreg_data = mm_coef_array[reg_if.rreg_no - REGISTER_COEF_BASE];
    end else begin
	reg_if.rreg_data = 32'h5052444F;
    end
  end
endmodule


module piradip_16x4sym (
    axi4mm_lite.SUBORDINATE axilite,
    axi4s.SUBORDINATE stream_in,
    axi4s.MANAGER stream_out
);
  localparam DATA_WIDTH = stream_in.data_width();

  localparam SAMPLE_WIDTH = 16;

  localparam NSAMPLES = DATA_WIDTH / SAMPLE_WIDTH;

  localparam NCOEF = 4;
  localparam COEF_WIDTH = 18;
  
  logic stream_active;

  always_comb stream_in.tready = 1'b1;
  always_comb stream_out.tvalid = 1'b1;

  logic [COEF_WIDTH*NCOEF-1:0] stream_coef;
  logic [COEF_WIDTH-1:0] c[NCOEF];

  always_comb begin
    integer i;
    for (i = 0; i < NCOEF; i++) begin
      c[i] = stream_coef[i*COEF_WIDTH+:COEF_WIDTH];
    end
  end

  piradip_fir_csr csrr(
    .aximm(axilite),
    .stream_rstn(stream_in.aresetn),
    .stream_clk(stream_in.aclk),
    .stream_update(stream_update),
    .stream_active(stream_active),
    .stream_coef(stream_coef)
  );

    
  logic [DATA_WIDTH-1:0] zn3;
  logic [DATA_WIDTH-1:0] zn2;
  logic [DATA_WIDTH-1:0] zn1;
  logic [DATA_WIDTH-1:0] z0;
  logic [DATA_WIDTH-1:0] z1;
  logic [DATA_WIDTH-1:0] z2;
  logic [DATA_WIDTH-1:0] z3;

  localparam FILTER_N = 3;
  

  logic clk;

  always_comb clk = stream_in.aclk;

  localparam NZZQ = 3;
  localparam SAMPLE_WINDOW = NSAMPLES * (NZZQ + 2);

  localparam NOW_OFFSET = NSAMPLES * NZZQ;
  
  // Save enough samples to 
  logic signed [15:0] samples[SAMPLE_WINDOW];
  
  always @(posedge clk) begin
    integer i;

    for (i = 0; i < SAMPLE_WINDOW - NSAMPLES; i++)
    begin
      samples[i] <= samples[i + NSAMPLES];
    end

    for (i = 0; i < NSAMPLES; i++)
    begin
      samples[SAMPLE_WINDOW-NSAMPLES+i] <= stream_in.tdata[i*SAMPLE_WIDTH+:SAMPLE_WIDTH];
    end
  end
  
  genvar n;

  logic [47:0] r[4][NSAMPLES];
  logic [47:0] sum[NSAMPLES];

  generate
    for (n = 0; n < NSAMPLES; n++) begin      
      piradip_addmul_zzz m3(
        .clk(clk),
	.rst(~stream_in.aresetn),
	.a1(samples[NOW_OFFSET + n + 3]),
	.a2(samples[NOW_OFFSET + n - 3]),
        .b(c[3]),
        .c(48'd0),
        .result(r[3][n])
      );

      piradip_addmul_zzz m2(
        .clk(clk),
	.rst(~stream_in.aresetn),
	.a1(samples[NOW_OFFSET + n + 2]),
	.a2(samples[NOW_OFFSET + n - 2]),
        .b(c[2]),
        .c(48'd0),
        .result(r[2][n])
      );

      piradip_addmul_zzz m1(
        .clk(clk),
	.rst(~stream_in.aresetn),
	.a1(samples[NOW_OFFSET + n + 1]),
	.a2(samples[NOW_OFFSET + n - 1]),
        .b(c[1]),
        .c(48'd0),
        .result(r[1][n])
      );

      always @(posedge clk) begin
	sum[n] <= r[3][n] + r[2][n] + r[1][n];
      end

      piradip_addmul_zzz m0(
        .clk(clk),
        .rst(~stream_in.aresetn),
        .a1(samples[n]),
	.a2({SAMPLE_WIDTH{1'b0}}),
        .b(c[0]),
	.c(sum[n]),
        .result(r[0][n])
      );

      always @(posedge clk) begin
	stream_out.tdata[SAMPLE_WIDTH*n+:SAMPLE_WIDTH] <= stream_active ? r[0][n][SAMPLE_WIDTH+:SAMPLE_WIDTH] : stream_in.tdata[SAMPLE_WIDTH*n+:SAMPLE_WIDTH];
      end
    end
  endgenerate
endmodule;
