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
    reg [WIDTH-1:0] data;

    reg active;
    reg mosi_r, miso_r;
    
    /* CPHA == 0 means that data is sampled on the first clock edge */

    always @(rstn)
    begin
        active <= 0;
        data <= INITIAL_VALUE;
    end
       

    wire clk_raw = sclk ^ CPOL;
    
    integer shift_count, latch_count;
    
    always @(negedge csn)
    begin
        active <= 1;
        $display("%s: SPI Transaction begin: %x", name, data);
        mosi_r <= 1'b0;
        miso_r <= data[WIDTH-1];
        shift_count = 0;
        latch_count = 0;
    end    

    generate
        if (CPHA == 0) begin
            assign miso = active ? data[WIDTH-1] : 1'bZ;
            
            always @(posedge clk_raw)
            begin
                if (active) begin
                    //$display("%s: %1d %1d %1d: LATCH %1d %1d %x", name, sclk, CPOL, CPHA, miso, mosi, data);
                    latch_count = latch_count + 1;
                    mosi_r <= mosi;
                end
            end
            
            always @(negedge clk_raw)
            begin
                if (active) begin
                    //$display("%s: %1d %1d %1d: SHIFT (%d) %1d %1d %x", name, sclk, CPOL, CPHA, shift_count, miso, mosi, data);
                    shift_count <= shift_count + 1;
                    data <= { data[WIDTH-2:0], mosi_r };
                end
            end
        end else begin
            assign miso = active ? miso_r : 1'bZ;        
        
            always @(posedge clk_raw)
            begin
                if (active) begin
                    //$display("%s: %1d %1d %1d: SHIFT (%d) %1d %1d %x", name, sclk, CPOL, CPHA, shift_count, miso, mosi, data);
                    shift_count <= shift_count + 1;
                    { miso_r, data } <= { data[WIDTH-1:0], 1'b0 };
                end
            end
            
            always @(negedge clk_raw)
            begin
                if (active) begin
                    //$display("%s: %1d %1d %1d: LATCH %1d %1d %x", name, sclk, CPOL, CPHA, miso, mosi, data);
                    latch_count = latch_count + 1;
                    data[0] <= mosi;
                end
            end                    
        end
    endgenerate

    always @(posedge csn)
    begin
        if (active) begin
            active <= 0;
            $display("%s: SPI Transaction end: %x shift_count: %d latch_count: %d", name, data, shift_count, latch_count);
        end
    end




endmodule
