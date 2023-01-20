`timescale 1ns / 1ps

module piradspi_fifo_engine #(
    parameter integer SEL_MODE = 1,
    parameter integer SEL_WIDTH = 8,
    parameter integer CMD_FIFO_DEPTH = 16,
    parameter integer DATA_FIFO_DEPTH = 64
) (
    piradspi_cmd_stream.SUBORDINATE cmd_stream,
    axi4s.SUBORDINATE               axis_mosi,
    axi4s.MANAGER                   axis_miso,

    output logic cmd_completed,
    output logic engine_error,
    output logic engine_busy,

    input  logic                 io_clk,
    input  logic                 io_rstn,
    output logic                 sclk,
    output logic                 mosi,
    input  logic                 miso,
    output logic [SEL_WIDTH-1:0] csn,
    output logic                 sel_active
);

  import piradspi_pkg::*;

  generate
    localparam MOSI_FIFO_WIDTH = $bits(axis_mosi.tdata);
    localparam MISO_FIFO_WIDTH = $bits(axis_miso.tdata);

    axi4s #(
        .WIDTH(MOSI_FIFO_WIDTH)
    ) f2e_mosi (
        .clk(io_clk),
        .resetn(io_rstn)
    );
    axi4s #(
        .WIDTH(MISO_FIFO_WIDTH)
    ) e2f_miso (
        .clk(io_clk),
        .resetn(io_rstn)
    );
  endgenerate

  piradspi_cmd_stream engine_stream (
      .clk(io_clk),
      .resetn(io_rstn)
  );


  piradspi_cmd_fifo cmd_fifo (
      .cmd_in (cmd_stream),
      .cmd_out(engine_stream.MANAGER)
  );

  piradip_axis_gearbox #(
      .DEPTH(DATA_FIFO_DEPTH)
  ) mosi_fifo (
      .in (axis_mosi),
      .out(f2e_mosi.MANAGER)
  );

  piradip_axis_gearbox #(
      .DEPTH(DATA_FIFO_DEPTH)
  ) miso_fifo (
      .in (e2f_miso.SUBORDINATE),
      .out(axis_miso)
  );


  piradspi_engine #(
      .SEL_MODE (SEL_MODE),
      .SEL_WIDTH(SEL_WIDTH)
  ) engine (
      .sclk(sclk),
      .mosi(mosi),
      .miso(miso),
      .sel_active(sel_active),
      .csn(csn),
      .cmd_completed(cmd_completed),
      .engine_error(engine_error),
      .engine_busy(engine_busy),
      .cmds_in(engine_stream.SUBORDINATE),
      .axis_mosi(f2e_mosi.SUBORDINATE),
      .axis_miso2(e2f_miso.MANAGER)
  );
endmodule

module piradspi_engine #(
    parameter integer SEL_MODE  = 1,
    parameter integer SEL_WIDTH = 8
) (
    piradspi_cmd_stream.SUBORDINATE cmds_in,

    axi4s.SUBORDINATE axis_mosi,
    axi4s.MANAGER     axis_miso2,

    output logic cmd_completed,
    output logic engine_error,
    output logic engine_busy,

    output logic                 sclk,
    output logic                 mosi,
    input  logic                 miso,
    output logic [SEL_WIDTH-1:0] csn,
    output logic                 sel_active
);
  import piradspi_pkg::*;

  localparam DATA_FIFO_WIDTH = axis_miso2.data_width();
  localparam RESPONSE_PAD_WIDTH = DATA_FIFO_WIDTH - $bits(response_t);


  typedef axis_miso2.data_t fifo_data_t;
  typedef cmds_in.command_t cmd_t;

  fifo_data_t data_word_t;

  typedef union packed {
    struct packed {
      response_t                     resp;
      logic [RESPONSE_PAD_WIDTH-1:0] pad;
    } r;
    fifo_data_t data;
  } response_u_t;

  cmd_t                 cur_cmd;

  logic [SEL_WIDTH-1:0] gen_sel;


  assign gen_sel = (SEL_MODE == 0) ? 1 << cur_cmd.device : cur_cmd.device;

  reg sclk_gen;
  wait_t sclk_cnt;
  assign sclk = sclk_gen ^ cur_cmd.cpol;

  response_u_t cur_data_out;

  typedef enum {
    IDLE = 0,
    FETCH1,
    WAIT_BEGIN_CMD,
    SELECT_DEVICE,
    LATCH,
    SHIFT,
    DESELECT_DEVICE,
    WAIT_END_CMD,
    END_CMD
  } state_t;

  state_t           state;

  reg        [31:0] state_cycles;
  wire              state_trigger;
  xfer_len_t        xfer_bits;

  piradip_state_timer state_timer (
      .rstn(cmds_in.aresetn),
      .clk(cmds_in.aclk),
      .state(state),
      .cycles(state_cycles),
      .trigger(state_trigger)
  );

  wire sclk_hold;  // Stretch SCLK to deal with flow control axis_cmd2 axis_cmd
  wire consume_cmd;

  wire mosi_bit_empty;
  wire miso_bit_full;

  assign consume_cmd = cmds_in.cmd_ready & cmds_in.cmd_valid;

  piradip_bit_stream mosi_stream (
      .clk(cmds_in.aclk),
      .resetn(cmds_in.aresetn)
  );
  piradip_bit_stream miso_stream (
      .clk(cmds_in.aclk),
      .resetn(cmds_in.aresetn)
  );

  piradip_stream_to_bit #(
      .WIDTH(DATA_FIFO_WIDTH)
  ) mosi_shift_reg (
      .align(cmd_completed),
      .empty(mosi_bit_empty),
      .bits_out(mosi_stream.MANAGER),
      .words_in(axis_mosi)
  );

  piradip_bit_to_stream #(
      .WIDTH(DATA_FIFO_WIDTH)
  ) miso_shift_reg (
      .align(cmd_completed),
      .full(miso_bit_full),
      .bits_in(miso_stream.SUBORDINATE),
      .words_out(axis_miso2)
  );

  assign mosi = mosi_stream.tdata;
  assign miso_stream.tdata = miso;
  assign cmd_completed = (state == END_CMD);

  assign cur_data_out.r.resp.magic = RESPONSE_MAGIC;
  assign cur_data_out.r.resp.id = cur_cmd.id;
  assign cur_data_out.r.pad = 0;

  assign sclk_hold = (mosi_stream.tready & ~mosi_stream.tvalid) || (~miso_stream.tready & miso_stream.tvalid);

  always @(posedge cmds_in.aclk) begin
    if (~cmds_in.aresetn) begin
      mosi_stream.tready <= 1'b0;
    end else if (mosi_stream.tready) begin
      // If we're here, this means we're waiting on a bit, so if we got one, great!
      if (mosi_stream.tvalid) begin
        mosi_stream.tready <= 1'b0;
      end
      // If not, well, we keep waiting
    end else if ((state == LATCH) && (sclk_cnt == 0)) begin
      mosi_stream.tready <= 1'b1;
    end
  end

  always_comb engine_busy = (state != IDLE);
  always_comb engine_error = 0;

  always @(posedge cmds_in.aclk) begin
    if (~cmds_in.aresetn) begin
      csn <= 0;
      sel_active <= 1'b0;
      state <= IDLE;
      cur_cmd.cpol <= 1'b0;
      cur_cmd.cpha <= 1'b0;
      cmds_in.cmd_ready <= 1'b0;
      miso_stream.tvalid <= 1'b0;
      xfer_bits <= 0;
      cur_cmd <= 0;
    end else begin
      case (state)
        IDLE: begin
          sclk_gen <= 1'b0;
          sel_active <= 1'b0;
          csn <= 0;

          if (consume_cmd) begin
            // Register command
            cmds_in.cmd_ready <= 1'b0;

            cur_cmd = cmds_in.cmd;
            state_cycles = cur_cmd.wait_start;
            sclk_cnt = cur_cmd.sclk_cycles;
            xfer_bits = cur_cmd.xfer_len;

            if (cur_cmd.wait_start) begin
              state <= WAIT_BEGIN_CMD;
            end else begin
              state <= SELECT_DEVICE;
              state_cycles <= cur_cmd.csn_to_sclk_cycles;
            end
          end else begin
            state <= IDLE;
            cmds_in.cmd_ready <= ~mosi_bit_empty & axis_miso2.tready;
          end
        end

        WAIT_BEGIN_CMD: begin
          if (state_trigger) begin
            state <= SELECT_DEVICE;
            state_cycles <= cur_cmd.csn_to_sclk_cycles;
          end else begin
            state <= WAIT_BEGIN_CMD;
          end
        end

        SELECT_DEVICE: begin
          csn <= gen_sel;
          sel_active <= 1'b1;
          if (state_trigger) begin
            if (cur_cmd.cpha == 1) begin
              state <= SHIFT;
            end else begin
              miso_stream.tvalid <= 1'b1;
              state <= LATCH;
            end

            sclk_gen <= ~sclk_gen;
          end else begin
            state <= SELECT_DEVICE;
          end
        end

        LATCH: begin
          if (miso_stream.tvalid & miso_stream.tready) begin
            miso_stream.tvalid <= 1'b0;
          end

          if (sclk_cnt != 0) begin
            sclk_cnt <= sclk_cnt - 1;
          end else if (~sclk_hold) begin
            if (cur_cmd.cpha == 1 && xfer_bits == 0) begin
              state_cycles <= cur_cmd.sclk_to_csn_cycles;
              state <= DESELECT_DEVICE;
            end else begin
              sclk_cnt <= cur_cmd.sclk_cycles;
              sclk_gen <= ~sclk_gen;
              state <= SHIFT;
            end
          end
        end

        SHIFT: begin
          if (sclk_cnt != 0) begin
            sclk_cnt <= sclk_cnt - 1;
          end else if (~sclk_hold) begin
            if (cur_cmd.cpha == 0 && xfer_bits == 1) begin
              state_cycles <= cur_cmd.sclk_to_csn_cycles;
              state <= DESELECT_DEVICE;
            end else begin
              xfer_bits <= xfer_bits - 1;
              miso_stream.tvalid <= 1'b1;
              miso_stream.tlast <= (xfer_bits == 1);
              sclk_cnt <= cur_cmd.sclk_cycles;
              sclk_gen <= ~sclk_gen;
              state <= LATCH;
            end
          end
        end

        DESELECT_DEVICE: begin
          if (state_trigger) begin
            state <= WAIT_END_CMD;
          end
        end

        WAIT_END_CMD: begin
          sel_active <= 1'b0;
          csn <= 0;
          state <= END_CMD;
        end

        END_CMD: begin
          state <= IDLE;
        end
      endcase
    end
  end
endmodule
