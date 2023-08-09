

package piradip_sample_buffer;
  localparam REGISTER_ID = 0;
  localparam REGISTER_CTRLSTAT = 1;

  localparam CTRLSTAT_ACTIVE = 0;
  localparam CTRLSTAT_ONE_SHOT = 1;
  localparam CTRLSTAT_Q_EN = 4;
  localparam CTRLSTAT_I_EN = 5;

  localparam REGISTER_START_OFFSET = 2;
  localparam REGISTER_END_OFFSET = 3;
  localparam REGISTER_STREAM_DEPTH = 4;
  localparam REGISTER_SIZE_BYTES = 5;
  localparam REGISTER_TRIGGER_COUNT = 6;
  localparam REGISTER_WRITE_COUNT = 7;
  localparam REGISTER_WRAP_COUNT = 8;
endpackage

module piradip_axis_sample_buffer_csr #(
    parameter BUFFER_BYTES = (1 << 16),
    parameter STREAM_OFFSET_WIDTH = 5,
    parameter DEBUG = 1
) (
    axi4mm_lite.SUBORDINATE aximm,

    input logic trigger,
    input logic stream_rstn,
    input logic stream_clk,
    input logic stream_stopped,
    input logic stream_wrap_toggle,
    output logic stream_update,
    output logic stream_active,
    output logic stream_one_shot,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_start_offset,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_end_offset,
    output logic i_en,
    output logic q_en
);
  localparam DATA_WIDTH = aximm.data_width();
  localparam ADDR_WIDTH = aximm.addr_width();
  localparam REGISTER_ADDR_BITS = ADDR_WIDTH - $clog2(DATA_WIDTH / 8);

  import piradip_sample_buffer::*;

  logic                           mm_update;
  logic                           mm_active;
  logic                           mm_one_shot;
  logic [STREAM_OFFSET_WIDTH-1:0] mm_start_offset;
  logic [STREAM_OFFSET_WIDTH-1:0] mm_end_offset;
  logic [DATA_WIDTH-1:0]          mm_trigger_count;
  logic [DATA_WIDTH-1:0]          mm_write_count;
  logic [DATA_WIDTH-1:0]          mm_wrap_count;

  localparam CDC_WIDTH = 2 + 2 * STREAM_OFFSET_WIDTH;

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
      .WIDTH(2 + 2 * STREAM_OFFSET_WIDTH)
  ) ctrl_cdc (
      .src_rst(~aximm.aresetn),
      .src_clk(aximm.aclk),
      .src_data({mm_one_shot, mm_active, mm_end_offset, mm_start_offset}),
      .src_send(mm_update),
      .dst_rst(~stream_rstn),
      .dst_clk(stream_clk),
      .dst_data({stream_one_shot, stream_active, stream_end_offset, stream_start_offset}),
      .dst_update(stream_update)
  );

  logic ctrl_stat_write;
  logic initialized;
  logic do_trigger, cur_trigger, last_trigger;
  
  always_comb
    ctrl_stat_write = aximm.aresetn && reg_if.wren && (reg_if.wreg_no == REGISTER_CTRLSTAT);
  
  always_comb
    cur_trigger = aximm.aresetn && (trigger | (ctrl_stat_write && reg_if.wreg_data[CTRLSTAT_ACTIVE]));

  always @(posedge aximm.aclk)
    last_trigger <= cur_trigger;
  

  always @(posedge aximm.aclk)
    mm_active <= cur_trigger & ~last_trigger;
  
  always @(posedge aximm.aclk) begin
    initialized <= ~aximm.aresetn ? 1'b0 : (initialized | mm_update);
    mm_update <= aximm.aresetn && (trigger | reg_if.wren | ~initialized);
  end

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      mm_trigger_count <= 0;
      mm_write_count <= 0;
    end else begin
      mm_trigger_count <= mm_active ? (mm_trigger_count + 1) : mm_trigger_count;
      mm_write_count <= reg_if.wren ? (mm_write_count + 1) : mm_write_count;      
    end
  end

  logic mm_i_en, mm_q_en;

  xpm_cdc_single i_en_cdc (
   .dest_out(i_en),
   .dest_clk(stream_clk),
   .src_clk(aximm.aclk),
   .src_in(mm_i_en)
  );

  xpm_cdc_single q_en_cdc (
   .dest_out(q_en),
   .dest_clk(stream_clk),
   .src_clk(aximm.aclk),
   .src_in(mm_q_en)
  );
  
  logic mm_wrap_toggle;
  
  xpm_cdc_single toggle_cdc (
   .dest_out(mm_wrap_toggle),
   .dest_clk(aximm.aclk),
   .src_clk(stream_clk),
   .src_in(stream_wrap_toggle)
  );
  
  logic last_toggle;
  
  always @(posedge aximm.aclk) begin
    last_toggle <= mm_wrap_toggle;

    if (~aximm.aresetn) begin
      mm_wrap_count <= 0;
    end else if (reg_if.wren && reg_if.wreg_no == REGISTER_WRAP_COUNT) begin
      mm_wrap_count <= 0;
    end else if (last_toggle != mm_wrap_toggle) begin
      mm_wrap_count <= mm_wrap_count + 1;
    end
  end
    
	     
  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      mm_start_offset <= 0;
      mm_end_offset <= (1 << STREAM_OFFSET_WIDTH) - 1;
      mm_one_shot <= 0;
      mm_i_en <= 1;
      mm_q_en <= 1;
    end else begin
      if (reg_if.wren) begin
        case (reg_if.wreg_no)
	  REGISTER_CTRLSTAT: begin
	    mm_one_shot <= reg_if.wreg_data[CTRLSTAT_ONE_SHOT];
	    mm_i_en <= reg_if.wreg_data[CTRLSTAT_I_EN];
	    mm_q_en <= reg_if.wreg_data[CTRLSTAT_Q_EN];
	  end
          REGISTER_START_OFFSET: mm_start_offset <= reg_if.mask_write_bytes(mm_start_offset);
          REGISTER_END_OFFSET:   mm_end_offset <= reg_if.mask_write_bytes(mm_end_offset);
        endcase
      end // if (reg_if.wren)
    end
  end // always @ (posedge aximm.aclk)

  always_comb begin
    case (reg_if.rreg_no)
      REGISTER_ID: begin
	reg_if.rreg_data = 32'h5053424F;
      end
      REGISTER_CTRLSTAT: begin
	reg_if.rreg_data = { 26'h0, mm_i_en, mm_q_en, cur_trigger, trigger, mm_one_shot, ~stream_stopped };
      end
      REGISTER_START_OFFSET: begin
	reg_if.rreg_data = mm_start_offset;
      end
      REGISTER_END_OFFSET: begin
	reg_if.rreg_data = mm_end_offset;
      end
      REGISTER_STREAM_DEPTH: begin
	reg_if.rreg_data = (1 << STREAM_OFFSET_WIDTH);
      end
      REGISTER_SIZE_BYTES: begin
	reg_if.rreg_data = BUFFER_BYTES;
      end
      REGISTER_TRIGGER_COUNT: begin
	reg_if.rreg_data = mm_trigger_count;
      end
      REGISTER_WRITE_COUNT: begin
	reg_if.rreg_data = mm_write_count;
      end
      REGISTER_WRAP_COUNT: begin
	reg_if.rreg_data = mm_wrap_count;
      end
      default: begin
	reg_if.rreg_data = 32'h5052444F;
      end
    endcase
  end
endmodule
