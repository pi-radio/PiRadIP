`timescale 1ns / 1ps

module piradip_stream_to_bit #(
    parameter WIDTH=32
) (
    input wire clk,
    input wire rstn,
    
    input wire align,
    
    output wire empty,
    input wire bit_ready,
    output wire bit_valid,
    output wire bit_data,
    
    output wire word_ready,
    input wire [WIDTH-1:0] word_data,
    input wire word_valid            
);
    localparam BIT_COUNT_WIDTH = $clog2(WIDTH+1);
    
    reg [WIDTH-1:0] shift_reg;
    reg [BIT_COUNT_WIDTH-1:0] bit_count;
    
    assign bit_data = shift_reg[WIDTH-1];
    
    assign word_read = word_ready & word_valid;
    assign bit_read = bit_ready & bit_valid;
    
    assign bit_valid = (bit_count != 0);
    assign empty = (bit_count == 0);
    
    assign word_ready = (bit_count == 1 && bit_read) || (bit_count == 0);
    
    always @(posedge clk)
    begin
        if (~rstn) begin
            bit_count <= 0;
            shift_reg <= 0;
        end else begin
            bit_count = 
                (align ? ((bit_count < WIDTH) ? 0 : WIDTH) : bit_count) +
                (word_read ? WIDTH : 0) -
                (bit_read ? 1 : 0);
  
            shift_reg = word_read ? (
                    (bit_count == 0) ? { word_data, 1'b0 } : { shift_reg[WIDTH], word_data }) :
                bit_read ? ( { shift_reg[WIDTH-1:0], 1'b0 } ) :
                shift_reg;
        end
    end   
endmodule

module piradip_bit_to_stream #(
    parameter WIDTH=32
) (
    input logic clk,
    input logic rstn,
    
    input logic align,
    output logic full,
    
    output logic bit_ready,
    input logic bit_valid,
    input logic bit_data,
    
    input logic word_ready,
    output logic [WIDTH-1:0] word_data,
    output logic word_valid            
);
    localparam BIT_COUNT_WIDTH = $clog2(WIDTH+1);
    
    logic [WIDTH:0] shift_reg;
    logic [BIT_COUNT_WIDTH-1:0] bit_count;

    assign bit_ready = (bit_count != 0);
    assign full = bit_count == 0;
    assign word_data = (bit_count == 0) ? shift_reg[WIDTH:1] : shift_reg[WIDTH-1:0];
    
    always @(posedge clk)
    begin
        if (~rstn) begin
            shift_reg = 0;
            bit_count = WIDTH + 1;
        end else begin
            if (align) begin
                bit_count = 1;
            end else if (word_valid & word_ready) begin
                bit_count = bit_count + WIDTH;
            end
            
            if(bit_ready && bit_valid) begin
                shift_reg = { shift_reg[WIDTH-1:0], bit_data };
                bit_count = bit_count - 1;
            end
        end
    end
    
    always @(posedge clk) word_valid = ~rstn ? 0 :
        (word_valid & word_ready) ? 0 :
        (align) ? 1 :
        word_valid;

endmodule