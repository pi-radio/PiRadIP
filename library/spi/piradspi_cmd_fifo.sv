
interface piradspi_cmd_stream (
    input logic clk,
    input logic resetn
);

  import piradspi_pkg::*;

  typedef struct packed {
    logic      cpol;
    logic      cpha;
    cmd_id_t   id;
    dev_id_t   device;
    wait_t     sclk_cycles;
    wait_t     wait_start;
    wait_t     csn_to_sclk_cycles;
    wait_t     sclk_to_csn_cycles;
    xfer_len_t xfer_len;
  } command_t;


  logic aclk, aresetn;

  logic     cmd_valid;
  logic     cmd_ready;
  command_t cmd;

  assign aclk = clk;
  assign aresetn = resetn;

  modport MANAGER(output cmd_valid, cmd, input aclk, aresetn, cmd_ready);

  modport SUBORDINATE(output cmd_ready, input aclk, aresetn, cmd, cmd_valid);
endinterface


module piradspi_cmd_fifo #(
    parameter integer CMD_FIFO_DEPTH = 16
) (
    piradspi_cmd_stream.SUBORDINATE cmd_in,
    piradspi_cmd_stream.MANAGER cmd_out
);

  generate
    localparam CMD_FIFO_WIDTH = 8 * ($bits(cmd_in.cmd) / 8 + (($bits(cmd_in.cmd) & 3'h7) ? 1 : 0));
  endgenerate

  axi4s cmd_in_axis (
      .clk(cmd_in.aclk),
      .resetn(cmd_in.aresetn)
  );
  axi4s cmd_out_axis (
      .clk(cmd_out.aclk),
      .resetn(cmd_out.aresetn)
  );

  assign cmd_in.cmd_ready = cmd_in_axis.tready;
  assign cmd_in_axis.tvalid = cmd_in.cmd_valid;
  assign cmd_in_axis.tdata = cmd_in.cmd;

  assign cmd_out_axis.tready = cmd_out.cmd_ready;
  assign cmd_out.cmd_valid = cmd_out_axis.tvalid;
  assign cmd_out.cmd = cmd_out_axis.tdata;

  piradip_axis_gearbox #(
      .DEPTH(CMD_FIFO_DEPTH)
  ) cmd_fifo (
      .in (cmd_in_axis.SUBORDINATE),
      .out(cmd_out_axis.MANAGER)
  );

endmodule
