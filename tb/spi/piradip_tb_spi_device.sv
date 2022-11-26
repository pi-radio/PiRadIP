`timescale 1ns / 1ps

module piradip_tb_spi_device #(
                              parameter CPOL = 0,
                              parameter CPHA = 0,
                              parameter WIDTH = 8,
                              parameter INITIAL_VALUE = 8'hBB,
                              parameter DEBUG = 0
                              ) (
                                 input logic  sclk,
                                 input logic  mosi,
                                 output logic miso,
                                 input logic  csn,
                                 input logic  rstn,
                                 input string name
                                 );
   logic [WIDTH-1:0]                          data;

   logic                                      clk_raw;

   assign clk_raw = sclk ^ CPOL;
   assign nclk_raw = ~clk_raw;

   integer                                    shift_count, latch_count;


   generate
      /* CPHA == 0 means that data is sampled on the first clock edge */
      if (CPHA == 0) begin
         assign miso = (~csn) ? data[WIDTH-1] : 1'bZ;
         logic mosi_r;

         always @(posedge clk_raw or posedge nclk_raw or negedge rstn or posedge csn)
           begin
              if (~rstn) begin
                 data <= INITIAL_VALUE;
              end else if(~csn) begin
                 if (clk_raw) begin
                    if (DEBUG) $display("%s: %1d %1d %1d: LATCH %1d %1d %x", name, sclk, CPOL, CPHA, miso, mosi, data);
                    latch_count = latch_count + 1;
                    mosi_r = mosi;
                 end else if (nclk_raw) begin
                    if (DEBUG) $display("%s: %1d %1d %1d: SHIFT (%d) %1d %1d %x", name, sclk, CPOL, CPHA, shift_count, miso, mosi, data);
                    shift_count = shift_count + 1;
                    data = { data[WIDTH-2:0], mosi_r };
                 end
              end else begin // if (~csn)
                 mosi_r <= 1'bX;
                 shift_count = 0;
                 latch_count = 0;
              end // else: !if(~csn)
           end
         always @(rstn or csn or clk_raw)
           begin
           end
      end else begin
         logic miso_r;
         assign miso = (~csn) ? miso_r : 1'bZ;

         always @(posedge clk_raw or posedge nclk_raw or negedge rstn or csn)
           begin
              if (~rstn) begin
                 data <= INITIAL_VALUE;
              end else if (~csn) begin
                 if ($rose(clk_raw)) begin
                    if (DEBUG) $display("%s: %1d %1d %1d: SHIFT (%d) %1d %1d %x", name, sclk, CPOL, CPHA, shift_count, miso, mosi, data);
                    shift_count <= shift_count + 1;
                    { miso, data } <= { data[WIDTH-1:0], 1'b0 };
                 end else if ($fell(clk_raw)) begin
                    if (DEBUG) $display("%s: %1d %1d %1d: LATCH %1d %1d %x", name, sclk, CPOL, CPHA, miso, mosi, data);
                    latch_count = latch_count + 1;
                    data[0] <= mosi;
                 end
              end else begin // if (~csn)
                 miso <= 1'bZ;
                 shift_count = 0;
                 latch_count = 0;
              end // else: !if(~csn)
           end
      end
   endgenerate

   always @(negedge csn) $display("%s: SPI Transaction begin: %x", name, data);
   always @(posedge csn) $display("%s: SPI Transaction end: %x shift_count: %d latch_count: %d", name, data, shift_count, latch_count);




endmodule
