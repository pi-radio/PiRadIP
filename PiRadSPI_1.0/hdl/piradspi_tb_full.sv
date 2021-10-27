`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/26/2021 12:34:44 PM
// Design Name: 
// Module Name: piradspi_tb_full
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


module piradspi_tb_full(

    );
    wire clk;
    reg rstn;
    
    localparam SEL_WIDTH=5;
    
    logic sclk, mosi, miso, csn_active;
    logic [SEL_WIDTH-1:0] csn_mode_1;  

    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    
    aximm_lite axilite_bus(.aclk(clk), .aresetn(rstn));
    
    PiRadSPI_v1_0 #(
        .C_SPI_SEL_MODE(1),
        .C_CSR_DATA_WIDTH(32),
        .C_CSR_ADDR_WIDTH(8),
        .C_SPI_SEL_WIDTH(SEL_WIDTH),
        .C_NUM_PROFILES(16)
    ) dut_sel_mode_1 (
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn_active(csn_active),
        .csn(csn_mode_1),
        .csr_awaddr(axilite_bus.awaddr),
        .csr_awprot(axilite_bus.awprot),
        .csr_awvalid(axilite_bus.awvalid),
        .csr_awready(axilite_bus.awready),
        .csr_wdata(axilite_bus.wdata),
        .csr_wstrb(axilite_bus.wstrb),
        .csr_wvalid(axilite_bus.wvalid),
        .csr_wready(axilite_bus.wready),
        .csr_bresp(axilite_bus.bresp),
        .csr_bvalid(axilite_bus.bvalid),
        .csr_bready(axilite_bus.bready),
        .csr_araddr(axilite_bus.araddr),
        .csr_arprot(axilite_bus.arprot),
        .csr_arvalid(axilite_bus.arvalid),
        .csr_arready(axilite_bus.arready),
        .csr_rdata(axilite_bus.rdata),
        .csr_rresp(axilite_bus.rresp),
        .csr_rvalid(axilite_bus.rvalid),
        .csr_rready(axilite_bus.rready)
    );

    piradip_tb_axilite_master master(.name("AXI"), .aximm(axilite_bus));

    initial 
    begin
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;

        clk_gen.sleep(5);
        
        rstn <= 1;
    end
endmodule
