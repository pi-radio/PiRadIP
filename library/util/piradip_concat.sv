`timescale 1ns / 1ps

module piradip_concat8 (
    output logic [7:0] dout,
    input logic din7,
    input logic din6,
    input logic din5,
    input logic din4,
    input logic din3,
    input logic din2,
    input logic din1,
    input logic din0
);
  assign dout = { din7, din6, din5, din4, din3, din3, din2, din1, din0 };
endmodule  // piradip_concat8

module piradip_concat16 (
    output logic [15:0] dout,
    input logic din15,
    input logic din14,
    input logic din13,
    input logic din12,
    input logic din11,
    input logic din10,
    input logic din9,
    input logic din8,
    input logic din7,
    input logic din6,
    input logic din5,
    input logic din4,
    input logic din3,
    input logic din2,
    input logic din1,
    input logic din0
);
  piradip_concat8 s0 (
      .dout  (dout[7:0]),
      .din7(din7),
      .din6(din6),
      .din5(din5),
      .din4(din4),
      .din3(din3),
      .din2(din2),
      .din1(din1),
      .din0(din0)
  );

  piradip_concat8 s1 (
      .dout  (dout[15:8]),
      .din7(din15),
      .din6(din14),
      .din5(din13),
      .din4(din12),
      .din3(din11),
      .din2(din10),
      .din1(din9),
      .din0(din8)
  );

endmodule  // piradip_concat16

module piradip_concat32 (
    output logic [31:0] dout,
    input logic din31,
    input logic din30,
    input logic din29,
    input logic din28,
    input logic din27,
    input logic din26,
    input logic din25,
    input logic din24,
    input logic din23,
    input logic din22,
    input logic din21,
    input logic din20,
    input logic din19,
    input logic din18,
    input logic din17,
    input logic din16,
    input logic din15,
    input logic din14,
    input logic din13,
    input logic din12,
    input logic din11,
    input logic din10,
    input logic din9,
    input logic din8,
    input logic din7,
    input logic din6,
    input logic din5,
    input logic din4,
    input logic din3,
    input logic din2,
    input logic din1,
    input logic din0
);

  piradip_concat16 s0 (
      .dout(dout[15:0]),
      .din15(din15),
      .din14(din14),
      .din13(din13),
      .din12(din12),
      .din11(din11),
      .din10(din10),
      .din9(din9),
      .din8(din8),
      .din7(din7),
      .din6(din6),
      .din5(din5),
      .din4(din4),
      .din3(din3),
      .din2(din2),
      .din1(din1),
      .din0(din0)
  );

  piradip_concat16 s1 (
      .dout(dout[31:16]),
      .din15(din31),
      .din14(din30),
      .din13(din29),
      .din12(din28),
      .din11(din27),
      .din10(din26),
      .din9(din25),
      .din8(din24),
      .din7(din23),
      .din6(din22),
      .din5(din21),
      .din4(din20),
      .din3(din19),
      .din2(din18),
      .din1(din17),
      .din0(din16)
  );

endmodule
