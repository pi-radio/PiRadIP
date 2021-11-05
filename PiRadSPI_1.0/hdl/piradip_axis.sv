`timescale 1ns / 1ps

interface axis_simple #(parameter WIDTH=32);
    localparam BYTE_WIDTH = WIDTH/8;
    localparam BYTE_MASK = {{BYTE_WIDTH}{1'b1}};

    logic tready, tvalid, tlast;
    logic [WIDTH-1:0] tdata;
    
    modport SUBORDINATE (input tvalid, tlast, tdata, output tready);
    modport MANAGER (output tvalid, tlast, tdata, input tready);
endinterface

