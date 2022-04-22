`timescale 1ns / 1ps

interface piradip_bit_stream #(
                               ) (
                                  input clk,
                                  input resetn
                                  );
   logic                                aclk, aresetn;
   logic                                tready, tvalid, tlast;
   logic                                tdata;

   assign aclk = clk;
   assign aresetn = resetn;
   
   modport SUBORDINATE (input tvalid, tlast, tdata, aclk, aresetn, output tready);
   modport MANAGER (output tvalid, tlast, tdata, input tready, aclk, aresetn);
endinterface

module piradip_stream_to_bit #(
                               parameter WIDTH=32
                               ) (
                                  input wire  align,
                                  output wire empty,
                                  axis_simple.SUBORDINATE words_in,
                                  piradip_bit_stream.MANAGER bits_out
                                  );
   localparam BIT_COUNT_WIDTH = $clog2(WIDTH+1);
   
   reg [WIDTH:0]                              shift_reg;
   reg [BIT_COUNT_WIDTH-1:0]                  bit_count;
   
   assign bits_out.tvalid = (bit_count != 0);
   assign bits_out.tdata = shift_reg[WIDTH];
   
   
   assign empty = (bit_count == 0);
   
   assign words_in.tready = (bit_count == 1 && (bits_out.tready & bits_out.tvalid)) || (bit_count == 0);
   
   always @(posedge words_in.aclk)
     begin
        if (~words_in.aresetn) begin
           bit_count = 0;
           shift_reg = 0;
           bits_out.tlast = 1'b0;
        end else if (align) begin
           bit_count = (bit_count < WIDTH) ? 0 : WIDTH;
           bits_out.tlast = 1'b1;
        end else begin
           if (bits_out.tvalid & bits_out.tready) begin
              bit_count = bit_count - 1;
              shift_reg = { shift_reg[WIDTH-1:0], 1'b0 };
              bits_out.tlast = (bit_count == 0);
           end
           
           if (words_in.tvalid & words_in.tready) begin
              shift_reg = (bit_count == 0) ? { words_in.tdata, 1'b0 } : { shift_reg[WIDTH], words_in.tdata };
              bit_count = WIDTH + bit_count;
           end
        end
     end   
endmodule

module piradip_bit_to_stream #(
                               parameter WIDTH=32
                               ) (
                                  input logic  align,
                                  output logic full,
                                  piradip_bit_stream.SUBORDINATE bits_in,
                                  axis_simple.MANAGER words_out
                                  );
   localparam BIT_COUNT_WIDTH = $clog2(WIDTH+1);
   
   logic [WIDTH:0]                             shift_reg;
   logic [BIT_COUNT_WIDTH-1:0]                 bit_count;

   assign bits_in.tready = (bit_count != 0);
   assign full = (bit_count == 0);
   assign words_out.tdata = (bit_count == 0) ? shift_reg[WIDTH:1] : shift_reg[WIDTH-1:0];
   assign words_out.tvalid = (bit_count <= 1);    
   assign words_out.tlast = 1'b0;
   
   always @(posedge bits_in.aclk)
     begin
        if (~bits_in.aresetn) begin
           shift_reg = 0;
           bit_count = WIDTH + 1;
        end else begin
           if (align) begin
              bit_count = 1;
           end else if (words_out.tvalid & words_out.tready) begin
              shift_reg = (bit_count == 0) ? { {{WIDTH-1}{1'b0}}, shift_reg[0] } : 0;
              bit_count = bit_count + WIDTH;
           end
           
           if(bits_in.tready && bits_in.tvalid) begin
              shift_reg = { shift_reg[WIDTH-1:0], bits_in.tdata };
              bit_count = bit_count - 1;
           end
        end
     end
endmodule
