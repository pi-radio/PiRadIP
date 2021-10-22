`timescale 1ns / 1ps



module piradip_SN74LVC1G139 (
        input wire A,
        input wire B,
        output wire [3:0] Y,
        output wire Y1,
        output wire Y2,
        output wire Y3
    );
    
    
    
    assign #4.90 Y = { ~(A & B), ~(~A & B),  ~(A & ~B), ~(~A & ~B) };
endmodule

module piradip_SN74LVC138A (
        input wire A,
        input wire B,
        input wire C,
        input wire G1,
        input wire G2A,
        input wire G2B,
        output wire [7:0] Y  
    );
    
    wire OE = ~(G1 & ~G2A & ~G2B);
    wire sel = { C, B, A };
    
    assign #5.90 Y = { ~(sel == 7 & ~OE), ~(sel == 6 & ~OE), ~(sel == 5 & ~OE),
        ~(sel == 4 & ~OE), ~(sel == 3 & ~OE), ~(sel == 2 & ~OE), ~(sel == 1 & ~OE),
        ~(sel == 0 & ~OE)};
endmodule

module piradip_SN74AUC125 (
        input [3:0] OEN,
        input [3:0] A,
        output [3:0] Y
    );
    
    assign #2.1 Y = ~OEN ? A : 1'bZ;
endmodule