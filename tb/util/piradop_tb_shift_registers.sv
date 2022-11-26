`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10/19/2021 04:41:25 PM
// Design Name:
// Module Name: piradop_tb_shift_registers
// Project Name:
// Target Devices:
// Tool Versions:
// Description:
//
// Dependencies:
//
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
//
//////////////////////////////////////////////////////////////////////////////////


module piradip_tb_shift_registers(

    );
    localparam WIDTH=32;

    wire clk;
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    reg rstn;


    reg align;
    reg bit_ready;

    wire bit_valid, bit_data;

    piradip_util_axis_manager #(.WIDTH(WIDTH)) words_in(.clk(clk_gen.clk), .aresetn(rstn), .name("WORDSIN"));
    piradip_util_axis_subordinate #(.WIDTH(WIDTH)) words_out(.clk(clk_gen.clk), .aresetn(rstn), .name("WORDSOUT"));


    piradip_stream_to_bit #(.WIDTH(WIDTH)) stream_to_bit(
        .clk(clk_gen.clk),
        .rstn(rstn),
        .align(align),
        .bit_ready(bit_ready),
        .bit_valid(bit_valid),
        .bit_data(bit_data),
        .word_ready(words_in.tready),
        .word_data(words_in.tdata),
        .word_valid(words_in.tvalid)
    );

    piradip_bit_to_stream #(.WIDTH(WIDTH)) bit_to_stream (
        .clk(clk_gen.clk),
        .rstn(rstn),
        .align(align),
        .bit_ready(bit_ready),
        .bit_valid(bit_valid),
        .bit_data(bit_data),
        .word_ready(words_out.tready),
        .word_data(words_out.tdata),
        .word_valid(words_out.tvalid)
    );


    integer bit_count;
    reg [127:0] shift_reg;

    always @(posedge clk_gen.clk)
    begin
        if (~rstn) begin
            bit_count = 0;
            shift_reg = 0;
        end else if(bit_ready & bit_valid) begin
            shift_reg = { shift_reg[126:0], bit_data };
            bit_count = bit_count + 1;
            if (bit_count % 8 == 0) begin
                $display("Shift register: %x", shift_reg);
            end
        end
    end


    initial
    begin
        rstn <= 0;
        bit_ready <= 0;
        align <= 0;

        clk_gen.sleep(5);

        rstn <= 1;

        clk_gen.sleep(1);

        words_in.send_one(32'hA5A5A5A5);

        clk_gen.sleep(10);

        clk_gen.sleep(40);

        words_in.send_one(32'hCCCCCCCC);
        clk_gen.sleep(4);
        words_in.send_one(32'hDDDDDDDD);

        clk_gen.sleep(100);
        $finish;
    end

endmodule
