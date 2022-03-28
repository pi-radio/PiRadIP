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

import piradspi::*;
import piradip_tb_aximm_util::*;     

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



    module piradspi_driver (axi4mm_lite.MANAGER axilite_bus);
        piradip_tb_axilite_manager manager(.aximm(axilite_bus));
        
        parameter REGISTER_BYTES = axilite_bus.DATA_WIDTH / 8;
        localparam POLL_CYCLES=100;
            
        typedef logic[axilite_bus.DATA_WIDTH-1:0] data_t;
        typedef logic[axilite_bus.ADDR_WIDTH-1:0] addr_t;        
        
        task automatic read_reg(input int no, ref data_t data);
            manager.read(no * REGISTER_BYTES, data);
        endtask

        task automatic write_reg(input int no, input data_t data);
            manager.write(no * REGISTER_BYTES, data);
        endtask

        task automatic set_bits_reg(input int no, input data_t bits);
            data_t v;
            manager.read(no * REGISTER_BYTES, v);
            manager.write(no * REGISTER_BYTES, v | bits);
        endtask

        task automatic clear_bits_reg(input int no, input data_t bits);
            data_t v;
            manager.read(no * REGISTER_BYTES, v);
            manager.write(no * REGISTER_BYTES, v & ~bits);
        endtask
        
        task automatic wait_bits_reg(input int no, input data_t bits);
            data_t v;
            
            read_reg(no, v);
            
            while((v & bits) != bits) begin
                repeat(POLL_CYCLES) @(posedge axilite_bus.aclk);
                read_reg(no, v);
            end;          
        endtask;
        
        task automatic wait_bit_no_reg(input int no, input int bit_no);
            wait_bits_reg(no, (1<<bit_no));
        endtask;
        
        task automatic check_device();
            data_t data;

            $display("Checking device version...");
                        
            read_reg(REGISTER_DEVID, data);
            assert(data == SPI_IP_MAGIC);

            read_reg(REGISTER_VER, data);
            assert(data == SPI_IP_VER);

            /* Check that device id is read only */            
            write_reg(REGISTER_DEVID, 0);
            read_reg(REGISTER_DEVID, data);
            assert(data == SPI_IP_MAGIC);
        endtask
        
        task automatic enable_intr(input logic enable);
            if (enable)
                set_bits_reg(REGISTER_CTRLSTAT, (1 << CTRLSTAT_INTREN));
            else
                clear_bits_reg(REGISTER_CTRLSTAT, (1 << CTRLSTAT_INTREN));
        endtask

        task automatic enable_engine(input logic enable);
            if (enable)
                set_bits_reg(REGISTER_CTRLSTAT, (1 << CTRLSTAT_ENABLE));
            else
                clear_bits_reg(REGISTER_CTRLSTAT, (1 << CTRLSTAT_ENABLE));
        endtask
        
        task automatic configure_profile(
            input data_t profile_no,
            input logic [1:0] pol_pha, 
            input data_t start_wait, 
            input data_t csn_to_sclk, 
            input data_t sclk_to_csn, 
            input data_t xferlen);
            
            int reg_base = REGISTER_PROFBASE + profile_no * REGISTER_PROFSIZE;
            
            write_reg(reg_base + REGISTER_POLPHA, pol_pha);
            write_reg(reg_base + REGISTER_STARTWAIT, start_wait);
            write_reg(reg_base + REGISTER_CSNTOSCLK, csn_to_sclk);
            write_reg(reg_base + REGISTER_SCLKTOCSN, sclk_to_csn);
            write_reg(reg_base + REGISTER_XFERLEN, xferlen);
        endtask
        
        task automatic start_spi_command(input data_t device, input data_t profile, input data_t cmd_id);
            write_reg(REGISTER_DEVSELECT, device);
            write_reg(REGISTER_PROFSELECT, profile);
            write_reg(REGISTER_CMD_ID, cmd_id);
            
            write_reg(REGISTER_TRIGGER, 1);
        endtask

        task automatic push_mosi(input data_t data);
            data_t res;
            
            wait_bit_no_reg(REGISTER_CTRLSTAT, CTRLSTAT_MOSIREADY);
            
            write_reg(REGISTER_MOSIFIFO, data);
        endtask

        task automatic wait_cmd(input data_t cmd_id);
            data_t res;
            
            wait_bit_no_reg(REGISTER_CTRLSTAT, CTRLSTAT_MISOREADY);
            
            read_reg(REGISTER_MISOFIFO, res);
            
            $display("MISO result: %x", res);
        endtask

        task automatic pop_miso(ref data_t res);
            wait_bit_no_reg(REGISTER_CTRLSTAT, CTRLSTAT_MISOREADY);
            
            read_reg(REGISTER_MISOFIFO, res);
        endtask
    
    
    endmodule
    
    piradspi_driver driver(axilite_bus);

    initial 
    begin
        logic [31:0] data;
        
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;                                                                           

        clk_gen.sleep(5);
        
        rstn <= 1;

        clk_gen.sleep(5);
        
        driver.check_device();
        driver.enable_intr(1);
        driver.enable_engine(1);

        driver.configure_profile(0, 0, 4, 4, 4, 24);        
        driver.configure_profile(1, 0, 4, 4, 4, 32);        
        driver.configure_profile(2, 0, 4, 4, 4, 40);        
        driver.configure_profile(3, 0, 4, 4, 4, 48);        
        
        driver.push_mosi(32'hA5A6A7A8);
        driver.start_spi_command(0, 0, 1);
        
        driver.push_mosi(32'hA1A2A3A4);
        driver.push_mosi(32'hA5A6A7A8);

        driver.start_spi_command(0, 3, 1);
        
        driver.wait_cmd(1);
        
        driver.pop_miso(data);
        $display("MISO: %x", data);
        driver.pop_miso(data);
        $display("MISO: %x", data);
        driver.pop_miso(data);
        $display("MISO: %x", data);
        driver.pop_miso(data);
        $display("MISO: %x", data);
        
/*        
        
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
        manager.write('h24, 'h00000000);
        manager.read('h8, data);
        */       
        $finish;
    end
endmodule
