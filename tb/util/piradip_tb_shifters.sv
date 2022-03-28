`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/24/2022 01:36:32 PM
// Design Name: 
// Module Name: piradip_tb_shifters
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


module piradip_tb_shifters(

    );
    
    wire clk;
    reg rstn;
    
    localparam WIDTH=32;
    localparam SHIFT_WIDTH = $clog2(WIDTH)+1;

    piradip_tb_clkgen clk_gen(.clk(clk));
    
    axis_simple #(.WIDTH(SHIFT_WIDTH+WIDTH)) words_in_if32(.clk(clk_gen.clk), .resetn(rstn));
    axis_simple #(.WIDTH(WIDTH)) words_out_if32(.clk(clk_gen.clk), .resetn(rstn));

    piradip_util_axis_manager #(.WIDTH(SHIFT_WIDTH+WIDTH)) words_in32(.manager_out(words_in_if32), .name("WORDSIN"));
    piradip_util_axis_subordinate #(.WIDTH(WIDTH)) words_out32(.sub_in(words_out_if32.SUBORDINATE), .name("WORDSOUT"));

    piradip_left_shift #(.DATA_WIDTH(WIDTH), .PIPELINE(1), .RECURSIVE(1)) left_shift(.data_in(words_in_if32.SUBORDINATE),
        .data_out(words_out_if32.MANAGER));
    
    logic [SHIFT_WIDTH-1:0] i;
    logic [WIDTH-1:0] result;
    
    localparam N = 32;
    
    initial 
    begin
        rstn <= 0;
        
        clk_gen.sleep(5);
        
        rstn <= 1;
        
        clk_gen.sleep(5);
        
        words_out32.ready();
        
        for (i = 0; i <= N; i++) begin
            words_in32.send_one({ i, {{WIDTH}{1'b1}}});
            //clk_gen.sleep(5);
        end
        words_in32.sync();
        
        for (i = 0; i <= N; i++) begin
            words_out32.recv_one(result);
            $display("%x", result);
        end 
        
        $finish;
    end
    
endmodule
