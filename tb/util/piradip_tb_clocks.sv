module piradip_tb_clkgen #(
    parameter integer HALF_PERIOD = 5  // Aligns with the default grid of Vivado
) (
    output reg clk
);
  timeunit 1ns;
  timeprecision 1ps;
  
  always #(HALF_PERIOD) clk <= ~clk;

  initial
  begin
    clk <= 0;
  end

  task sleep(input int n);
    repeat (n) @(posedge clk);
  endtask;
endmodule

