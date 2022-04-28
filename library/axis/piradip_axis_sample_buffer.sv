

package piradip_sample_buffer;
  localparam REGISTER_CTRLSTAT = 0;

  localparam CTRLSTAT_ACTIVE = 0;
  localparam CTRLSTAT_ONE_SHOT = 1;

  localparam REGISTER_START_OFFSET = 1;
  localparam REGISTER_END_OFFSET = 2;
endpackage

module piradip_axis_sample_buffer_csr #(
    parameter STREAM_OFFSET_WIDTH = 5,
    parameter DEBUG = 1
) (
    axi4mm_lite.SUBORDINATE aximm,

    input logic trigger,
    input logic stream_rstn,
    input logic stream_clk,
    input logic stream_stopped,
    output logic stream_update,
    output logic stream_active,
    output logic stream_one_shot,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_start_offset,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_end_offset
);
  localparam DATA_WIDTH = $bits(aximm.rdata);
  localparam ADDR_WIDTH = $bits(aximm.araddr);
  localparam REGISTER_ADDR_BITS = ADDR_WIDTH - $clog2(DATA_WIDTH / 8);

  import piradip_sample_buffer::*;

  logic                           mm_update;
  logic                           mm_active;
  logic                           mm_one_shot;
  logic [STREAM_OFFSET_WIDTH-1:0] mm_start_offset;
  logic [STREAM_OFFSET_WIDTH-1:0] mm_end_offset;

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
      .WIDTH(2)
  ) ctrl_cdc (
      .src_rst(~aximm.aresetn),
      .src_clk(aximm.aclk),
      .src_data({mm_one_shot, mm_active}),
      .src_send(mm_update),
      .dst_rst(~stream_rstn),
      .dst_clk(stream_clk),
      .dst_data({stream_one_shot, stream_active}),
      .dst_update(stream_update)
  );

  piradip_cdc_auto_reg #(
      .WIDTH(2 * STREAM_OFFSET_WIDTH)
  ) offset_cdc (
      .src_rst (~aximm.aresetn),
      .src_clk (aximm.aclk),
      .src_data({mm_end_offset, mm_start_offset}),
      .dst_rst (~stream_rstn),
      .dst_clk (stream_clk),
      .dst_data({stream_end_offset, stream_start_offset})
  );

  function automatic update_flag(ref logic flag, input logic newval);
    if (flag != newval) begin
      flag = newval;
      mm_update = 1'b1;
    end
  endfunction

  logic initialized;

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      initialized = 1'b0;
      mm_update = 1'b0;
      mm_active = 1'b0;
      mm_one_shot = 1'b0;
      mm_start_offset = 0;
      mm_end_offset = {STREAM_OFFSET_WIDTH{1'b1}};
    end else begin
      mm_update   = ~initialized;
      initialized = 1'b1;

      if (trigger) update_flag(mm_active, 1'b1);

      if (reg_if.wren) begin
        case (reg_if.wreg_no)
          REGISTER_CTRLSTAT: begin
            if (reg_if.wstrb[0]) begin
              update_flag(mm_active, reg_if.wreg_data[CTRLSTAT_ACTIVE]);
              update_flag(mm_one_shot, reg_if.wreg_data[CTRLSTAT_ONE_SHOT]);
            end
          end
          REGISTER_START_OFFSET: mm_start_offset = reg_if.mask_write_bytes(mm_start_offset);
          REGISTER_END_OFFSET:   mm_start_offset = reg_if.mask_write_bytes(mm_end_offset);
        endcase
      end
    end
  end
endmodule
