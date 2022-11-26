module piradip_single_trigger #(
    parameter COUNTER_WIDTH = 32
) (
    input  logic                     clk,
    input  logic                     rstn,
    input  logic [COUNTER_WIDTH-1:0] wait_cycles,
    input  logic                     arm,
    output logic                     armed,
    output logic                     trigger
);

  logic [COUNTER_WIDTH-1:0] counter;

  always @(posedge clk) begin
    if (~rstn) begin
      trigger <= 1'b0;
      armed   <= 1'b0;
    end else if (armed) begin
      if (arm) begin
        trigger <= 1'b1;
        counter <= wait_cycles;
      end else if (counter > 0) begin
        trigger <= 1'b0;
        counter <= counter - 1;
      end else begin
        trigger <= 1'b1;
        armed   <= 1'b0;
      end
    end else begin  // if (armed)
      trigger <= 1'b0;
      if (arm) begin
        armed   <= 1'b1;
        counter <= wait_cycles;
      end
    end
  end

endmodule


module piradip_trigger_unit #(
    parameter N_TRIGGER = 32
) (
    axi4mm_lite.SUBORDINATE axilite,
    output logic [N_TRIGGER-1:0] triggers
);

  localparam REGISTER_ID = 0;
  localparam REGISTER_TRIGGER_MASK = 1;
  localparam REGISTER_TRIGGER = 2;
  localparam REGISTER_DELAY_BASE = 3;

  localparam DATA_WIDTH = $bits(axilite.rdata);
  localparam ADDR_WIDTH = $bits(axilite.araddr);
  localparam REGISTER_ADDR_BITS = ADDR_WIDTH - $clog2(DATA_WIDTH / 8);

  logic                  arm;

  logic [ N_TRIGGER-1:0] armed;
  logic [ N_TRIGGER-1:0] trigger_raw;
  logic [ N_TRIGGER-1:0] trigger_mask;
  logic [DATA_WIDTH-1:0] delay_reg    [N_TRIGGER-1:0];

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

  assign triggers = trigger_raw & trigger_mask;

  always @(posedge axilite.aclk) begin
    if (~axilite.aresetn)
      trigger_mask <= (1 << N_TRIGGER) - 1;
    else if (reg_if.is_reg_write(REGISTER_TRIGGER_MASK))
      trigger_mask <= reg_if.wreg_data;
  end

  always @(posedge axilite.aclk) begin
    arm <= (axilite.aresetn & reg_if.is_reg_write(REGISTER_TRIGGER));
  end


  always_comb begin
    if (reg_if.rreg_no >= REGISTER_DELAY_BASE &&
            reg_if.rreg_no < REGISTER_DELAY_BASE + N_TRIGGER) begin
      reg_if.rreg_data = delay_reg[reg_if.rreg_no-REGISTER_DELAY_BASE];
    end else begin
      case (reg_if.rreg_no)
	REGISTER_ID: reg_if.rreg_data 		= 32'h50545247;
        REGISTER_TRIGGER_MASK: reg_if.rreg_data = trigger_mask;
        REGISTER_TRIGGER: reg_if.rreg_data 	= &armed;
	default: reg_if.rreg_data               = 32'h5052444F;
      endcase  // case (reg_if.rreg_no)
    end
  end

  genvar i;

  generate
    for (i = 0; i < N_TRIGGER; i++) begin
      piradip_single_trigger #(
          .COUNTER_WIDTH(DATA_WIDTH)
      ) trigger (
          .clk(axilite.aclk),
          .rstn(axilite.aresetn),
          .arm(arm),
          .wait_cycles(delay_reg[i]),
          .armed(armed[i]),
          .trigger(trigger_raw[i])
      );

      always @(posedge axilite.aclk) begin
        if (~axilite.aresetn) begin
          delay_reg[i] = 0;
        end else if (reg_if.is_reg_write(REGISTER_DELAY_BASE + i)) begin
          delay_reg[i] = reg_if.wreg_data;
        end
      end
    end
  endgenerate

endmodule
