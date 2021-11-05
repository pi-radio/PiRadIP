`timescale 1ns / 1ps

module piradspi_tb_csr(

    );
    wire clk;
    reg  rstn;
    
    axi4mm_lite #(.ADDR_WIDTH(8), .DATA_WIDTH(32)) axilite(.aclk(clk), .aresetn(rstn));
    
    axis_simple axis_cmd();
    axis_simple axis_mosi();
    axis_simple axis_miso();
    
    piradip_util_axis_subordinate slave_cmd(.clk(clk), .aresetn(rstn), .subordinatein(axis_cmd.SUBORDINATE));    
    
    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));
    
    piradip_tb_axilite_manager manager(.name("AXI Master"), .aximm(axilite.MANAGER));
        
    piradspi_csr csr(.aximm(axilite.SUBORDINATE), .axis_cmd(axis_cmd.MANAGER), 
            .axis_mosi(axis_mosi.MANAGER), .axis_miso(axis_miso.SUBORDINATE));
    
    initial 
    begin
        logic [31:0] data;
        
        $timeformat(-9, 2, " ns", 0);
        rstn <= 0;

        clk_gen.sleep(5);
        
        rstn <= 1;
        
        clk_gen.sleep(5);
        
        manager.read('h0, data);
        manager.read('h4, data);
        
        manager.write('h0, 'h0);
        
        manager.read('h0, data);
        manager.write('h40, 'b11);
        manager.write('h44, 'd5);
        manager.write('h48, 'd10);
        manager.write('h4C, 'd15);
        manager.write('h40, 'd20);
        manager.write('h44, 'd64);

        manager.write('h3C, 'd0);

        clk_gen.sleep(40);

        $finish;
    end    
    
    
endmodule
