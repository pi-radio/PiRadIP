`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company:
// Engineer:
//
// Create Date: 10/19/2021 02:06:37 PM
// Design Name:
// Module Name: piradio_v2_tb_spi_decoder
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


module piradio_v2_tb_daughter_card(
    input rstn,
    input mosi,
    output miso,
    input sclk,
    input seln,
    input carden,
    input [2:0] device_sel);

    wire [7:0] spics_out;

    piradip_SN74AUC125 buffer(.oen(buf_enn),
        .A({mosi, card_miso, sclk, seln}),
        .Y({card_mosi, miso, card_sclk, card_seln}));

    piradip_SN74LVC138A decoder(.G1(carden), .G2A(card_seln), .G2B(1'b0),
        .A(device_sel[0]), .B(device_sel[1]), .C(device_sel[2]),
        .Y(spics_out));

    piradip_tb_spi_slave #(
        .CPOL(0), .CPHA(0), .WIDTH(8), .INITIAL_VALUE(0)
    ) slv1 (
        .sclk(card_sclk),
        .mosi(card_mosi),
        .miso(card_miso),
        .csn(spics_out[0]),
        .rstn(rstn),
        .name("SYNTH0")
    );

endmodule

module piradio_v2_tb_spi_decoder(
        input rstn,
        input mosi,
        output miso,
        input sclk,
        input [1:0] card_sel
    );

    wire [3:0] spi_cs_card;

    piradip_SN74LVC1G139 card_decoder(.A(card_sel[0]), .B(card_sel[1]),
        .Y0(spi_cs_card[0]), .Y1(spi_cs_card[1]), .Y2(spi_cs_card[2]), .Y3(spi_cs_card[3]));

    piradio_v2_tb_daughter_card card0(.rstn(rstn), .mosi(mosi), .miso(miso), .sclk(sclk), .seln(spi_cs_card[0]));

endmodule
