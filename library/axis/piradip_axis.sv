`timescale 1ns / 1ps

interface axis_simple #(
    parameter integer WIDTH = 32
) (
    input logic clk,
    input logic resetn
);
  localparam BYTE_WIDTH = WIDTH / 8;
  localparam BYTE_MASK = {{BYTE_WIDTH} {1'b1}};

  typedef logic [WIDTH-1:0] data_t;


  function data_width();
     data_width = WIDTH;
  endfunction

  logic aclk, aresetn;
  logic tready, tvalid, tlast;
  data_t tdata;

  assign aclk = clk;
  assign aresetn = resetn;

  modport SUBORDINATE(import data_width, input tvalid, tlast, tdata, aclk, aresetn, output tready);
  modport MANAGER(import data_width, output tvalid, tlast, tdata, input tready, aclk, aresetn);
endinterface

interface axi4s #(
    parameter integer WIDTH = 32,
    parameter integer ID_WIDTH = 0,
    parameter integer DEST_WIDTH = 0,
    parameter integer USER_WIDTH = 0
) (
    input logic clk,
    input logic resetn
);
  localparam BYTE_WIDTH = WIDTH / 8;
  localparam BYTE_MASK = {BYTE_WIDTH{1'b1}};

  typedef logic [WIDTH-1:0] data_t;
  typedef logic [BYTE_WIDTH-1:0] strb_t;
  typedef logic [ID_WIDTH-1:0] id_t;
  typedef logic [DEST_WIDTH-1:0] dest_t;
  typedef logic [USER_WIDTH-1:0] user_t;

  function integer data_width();
     return WIDTH;
  endfunction


  logic aclk, aresetn;
  logic tready, tvalid, tlast;
  data_t tdata;
  strb_t tstrb;
  strb_t tkeep;
  id_t   tid;
  dest_t tdest;
  user_t tuser;

  assign aclk = clk;
  assign aresetn = resetn;

  modport SUBORDINATE(
      import data_width,
      input  tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser, aclk, aresetn,
      output tready
  );
  modport MANAGER(
      import data_width,
      output tvalid, tlast, tdata, tstrb, tkeep, tid, tdest, tuser,
      input tready, aclk, aresetn
  );
endinterface
