`timescale 1ns / 1ps

module piradip_state_timer #(parameter integer REG_WIDTH=32) (
    input wire rstn,
    input wire clk,
    input wire [REG_WIDTH-1:0] state,
    input wire [REG_WIDTH-1:0] cycles,
    output wire trigger
);
    reg [REG_WIDTH-1:0] old_state;
    reg [REG_WIDTH-1:0] counter;
    
    assign trigger = ((state == old_state) && (counter == 0)) || ((state != old_state) && (cycles == 0));
    
    always @(posedge clk)
    begin
        if (~rstn) begin
            counter <= 0;
            old_state <= 0;                
        end else begin
            old_state <= state;
            if (state != old_state) begin
                counter <= (cycles > 0) ? cycles - 1 : 0;
            end else if (counter > 0) begin
                counter <= counter - 1;
            end
        end
    end
endmodule
