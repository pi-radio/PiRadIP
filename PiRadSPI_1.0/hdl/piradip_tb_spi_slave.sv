`timescale 1ns / 1ps

module piradip_tb_spi_slave #(
    parameter CPOL = 0,
    parameter CPHA = 0,
    parameter WIDTH = 8,
    parameter INITIAL_VALUE = 8'hBB
) (
    input sclk,
    input mosi,
    output miso,
    input csn,
    input rstn,
    input string name
);

    reg [WIDTH-1:0] shift_reg;
    reg mosi_r;
    reg miso_r;
    wire pha = sclk ^ CPOL ^ CPHA;
    
    assign miso = (~rstn || csn) ? 1'bZ :
                  (pha == 0) ? shift_reg[WIDTH-1] :
                  miso;

    always @(negedge csn)
    begin
        $display("%s: SPI Transaction begin: %x", name, shift_reg);
        miso_r <= shift_reg[WIDTH-1];
    end
    
    always @(posedge pha)
    begin
        if (~csn) begin
            mosi_r <= mosi;
        end
    end
    
    always @(negedge pha)
    begin
        if (~csn) begin 
            miso_r <= shift_reg[WIDTH-1];
            shift_reg <= { shift_reg[WIDTH-2:0], mosi_r };
        end
    end
    
    always @(posedge csn)
    begin
        $display("%s: SPI Transaction end: %x", name, shift_reg);
    end

    initial
    begin
        shift_reg = { 1'b0, INITIAL_VALUE };
        miso_r = 1'bX;
        mosi_r = 1'bX;
    end

endmodule
