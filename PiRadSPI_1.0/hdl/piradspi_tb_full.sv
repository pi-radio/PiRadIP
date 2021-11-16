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
    
    axi4mm_lite axilite_bus(.clk(clk), .resetn(rstn));
    
    piradip_tb_spi_slave #(
        .WIDTH(64),
        .CPOL(0),
        .CPHA(0),
        .INITIAL_VALUE(64'h01020304_05060708)
    ) slave_00 (
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .csn(~(csn_active && (csn_mode_1 == 0))),
        .name("Slave 00")
    );
    
    logic interrupt_sel_mode_1;
    
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
        .interrupt(interrupt_sel_mode_1),
        .csn_active(csn_active),
        .csn(csn_mode_1),
        .csr_aclk(clk),
        .csr_aresetn(rstn),
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

    piradip_tb_axilite_manager manager(.name("AXI"), .aximm(axilite_bus));

    initial 
    begin
        logic [31:0] data;
        
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;                                                                           

        clk_gen.sleep(5);
        
        rstn <= 1;

        clk_gen.sleep(5);
        
        manager.read(0, data);
        manager.read('h4, data);
        // Enable Interrupts and Engine
        manager.write('h8, 'h00000021);
        
        manager.write('h0, 'h0);
        
        manager.write('h18, 'h01020304);
        manager.read('h18, data);
        manager.write('h18, 'h05060708);
        manager.read('h18, data);
        
        manager.read('h0, data);
        manager.write('h40, 'b11);
        manager.write('h44, 'd5);
        manager.write('h48, 'd10);
        manager.write('h4C, 'd15);
        manager.write('h40, 'd20);
        manager.write('h44, 'd64);

        manager.write('h3C, 'd0);
        
        wait(interrupt_sel_mode_1 == 1);

        manager.read('h1C, data);
        manager.read('h1C, data);
        manager.read('h1C, data);
        manager.read('h1C, data);

        // Acknowledge interrupt
        manager.read('h8, data);
        assert(data & 
        manager.write('h24, 'h00000000);
        manager.read('h8, data);
               
        $finish;
    end
endmodule
