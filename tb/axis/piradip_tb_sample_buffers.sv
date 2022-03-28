`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/28/2022 04:18:32 PM
// Design Name: 
// Module Name: piradip_tb_sample_buffers
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


module piradip_tb_sample_buffers(

    );
    wire clk;
    reg rstn;

    piradip_tb_clkgen clk_gen(.clk(clk));
        
    axi4mm axi4_data(.clk(clk), .resetn(rstn));
    
    piradip_axi4_imp #(
        ) axi4imp (
            .aximm(axi4_data.SUBORDINATE)
        );
    
    initial 
    begin
        rstn <= 0;
        
        clk_gen.sleep(5);
        
        rstn <= 1;
        
        clk_gen.sleep(5);
    end    
    
endmodule
