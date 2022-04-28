`timescale 1ns / 1ps

module piradip_slice8 (
    input logic [7:0] din,
    output logic dout7,
    output logic dout6,
    output logic dout5,
    output logic dout4,
    output logic dout3,
    output logic dout2,
    output logic dout1,
    output logic dout0
);
  assign dout0 = din[0];
  assign dout1 = din[1];
  assign dout2 = din[2];
  assign dout3 = din[3];
  assign dout4 = din[4];
  assign dout5 = din[5];
  assign dout6 = din[6];
  assign dout7 = din[7];
endmodule  // piradip_slice16

module piradip_slice16 (
    input logic [15:0] din,
    output logic dout15,
    output logic dout14,
    output logic dout13,
    output logic dout12,
    output logic dout11,
    output logic dout10,
    output logic dout9,
    output logic dout8,
    output logic dout7,
    output logic dout6,
    output logic dout5,
    output logic dout4,
    output logic dout3,
    output logic dout2,
    output logic dout1,
    output logic dout0
);
  piradip_slice8 s0 (
      .din  (din[7:0]),
      .dout7(dout7),
      .dout6(dout6),
      .dout5(dout5),
      .dout4(dout4),
      .dout3(dout3),
      .dout2(dout2),
      .dout1(dout1),
      .dout0(dout0)
  );

  piradip_slice8 s1 (
      .din  (din[15:8]),
      .dout7(dout15),
      .dout6(dout14),
      .dout5(dout13),
      .dout4(dout12),
      .dout3(dout11),
      .dout2(dout10),
      .dout1(dout9),
      .dout0(dout8)
  );

endmodule  // piradip_slice16

module piradip_slice32 (
    input logic [31:0] din,
    output logic dout31,
    output logic dout30,
    output logic dout29,
    output logic dout28,
    output logic dout27,
    output logic dout26,
    output logic dout25,
    output logic dout24,
    output logic dout23,
    output logic dout22,
    output logic dout21,
    output logic dout20,
    output logic dout19,
    output logic dout18,
    output logic dout17,
    output logic dout16,
    output logic dout15,
    output logic dout14,
    output logic dout13,
    output logic dout12,
    output logic dout11,
    output logic dout10,
    output logic dout9,
    output logic dout8,
    output logic dout7,
    output logic dout6,
    output logic dout5,
    output logic dout4,
    output logic dout3,
    output logic dout2,
    output logic dout1,
    output logic dout0
);

  piradip_slice16 s0 (
      .din(din[15:0]),
      .dout15(dout15),
      .dout14(dout14),
      .dout13(dout13),
      .dout12(dout12),
      .dout11(dout11),
      .dout10(dout10),
      .dout9(dout9),
      .dout8(dout8),
      .dout7(dout7),
      .dout6(dout6),
      .dout5(dout5),
      .dout4(dout4),
      .dout3(dout3),
      .dout2(dout2),
      .dout1(dout1),
      .dout0(dout0)
  );

  piradip_slice16 s1 (
      .din(din[31:16]),
      .dout15(dout31),
      .dout14(dout30),
      .dout13(dout29),
      .dout12(dout28),
      .dout11(dout27),
      .dout10(dout26),
      .dout9(dout25),
      .dout8(dout24),
      .dout7(dout23),
      .dout6(dout22),
      .dout5(dout21),
      .dout4(dout20),
      .dout3(dout19),
      .dout2(dout18),
      .dout1(dout17),
      .dout0(dout16)
  );

endmodule
