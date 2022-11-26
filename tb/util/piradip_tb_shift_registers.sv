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
    wire clk;
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    reg rstn;


    reg align32;

    piradip_bit_stream bit_stream32(.clk(clk_gen.clk), .resetn(rstn));
    piradip_bit_stream bit_stream12(.clk(clk_gen.clk), .resetn(rstn));

    axis_simple words_in_if32(.clk(clk_gen.clk), .resetn(rstn));
    axis_simple words_out_if32(.clk(clk_gen.clk), .resetn(rstn));

    piradip_util_axis_manager #(.WIDTH(32)) words_in32(.manager_out(words_in_if32.MANAGER), .name("WORDSIN"));
    piradip_util_axis_subordinate #(.WIDTH(32)) words_out32(.sub_in(words_out_if32.SUBORDINATE), .name("WORDSOUT"));

    piradip_stream_to_bit #(.WIDTH(32)) stream_to_bit32(
        .clk(clk_gen.clk),
        .rstn(rstn),
        .align(align32),
        .bits_out(bit_stream32.MANAGER),
        .words_in(words_in_if32.SUBORDINATE)
    );

    piradip_bit_to_stream #(.WIDTH(32)) bit_to_stream32 (
        .clk(clk_gen.clk),
        .rstn(rstn),
        .align(align32),
        .bits_in(bit_stream32.SUBORDINATE),
        .words_out(words_out_if32.MANAGER)
    );

    integer bit_count;
    reg [127:0] shift_reg;

    always @(posedge clk_gen.clk)
    begin
        if (~rstn) begin
            bit_count = 0;
            shift_reg = 0;
        end else if(bit_stream32.tready & bit_stream32.tvalid) begin
            shift_reg = { shift_reg[126:0], bit_stream32.tdata };
            bit_count = bit_count + 1;
            if (bit_count % 8 == 0) begin
                $display("Shift register: %x", shift_reg);
            end
        end
    end

    task automatic test32();
        logic [31:0] result;

        wait(rstn == 1);

        clk_gen.sleep(1);

        words_in32.send_one(32'hA5A5A5A5);

        words_out32.recv_one(result);
        assert(result == 32'hA5A5A5A5);

        clk_gen.sleep(40);

        // test flow control

        words_in32.send_one(32'hCCCCCCCC);
        words_in32.send_one(32'hDDDDDDDD);

        words_out32.recv_one(result);

        assert(result == 32'hCCCCCCCC);

        words_out32.recv_one(result);

        assert(result == 32'hDDDDDDDD);


        clk_gen.sleep(100);
    endtask

    initial
    begin
        rstn <= 0;
        align32 <= 0;

        clk_gen.sleep(5);

        rstn <= 1;


        fork
            test32();
        join



        $finish;
    end

endmodule
