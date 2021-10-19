`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/18/2021 08:02:49 PM
// Design Name: 
// Module Name: piradip_spi_slave
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


module piradip_tb_spi_slave #(
    parameter CPOL = 0,
    parameter CPHA = 0,
    parameter WIDTH = 8
)(
    input sclk,
    input mosi,
    output miso,
    input csn,
    input rstn
    );
endmodule
