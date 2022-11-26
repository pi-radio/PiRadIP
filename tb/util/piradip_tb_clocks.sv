`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10/15/2021 01:58:55 PM
// Design Name:
// Module Name: piradip_tb_clocks
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


module piradip_tb_clkgen #(
    parameter integer HALF_PERIOD = 5  // Aligns with the default grid of Vivado
) (
    output reg clk
);
    always #(HALF_PERIOD) clk <= ~clk;

    initial
    begin
        clk <= 0;
    end

    task sleep(input int n);
        repeat (n) @(posedge clk);
    endtask;
endmodule

