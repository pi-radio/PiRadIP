`timescale 1ns / 1ps

`include "piradspi.svh"

import piradspi::*;

module piradspi_tb_csr(

    );
    wire clk;
    reg  rstn;

    axi4mm_lite #(.ADDR_WIDTH(8), .DATA_WIDTH(32)) axilite(.clk(clk), .resetn(rstn));

    axis_simple #(.WIDTH(CMD_FIFO_WIDTH)) axis_cmd(.clk(clk), .resetn(rstn));
    axis_simple axis_mosi(.clk(clk), .resetn(rstn));
    axis_simple axis_miso(.clk(clk), .resetn(rstn));

    piradip_util_axis_inc_manager manager_miso(.name("MISO MANAGER"), .manager_out(axis_miso.MANAGER));

    piradip_util_axis_subordinate slave_cmd(.name("CMD SLAVE"), .sub_in(axis_cmd.SUBORDINATE));
    piradip_util_axis_subordinate slave_mosi(.name("MOSI SLAVE"), .sub_in(axis_mosi.SUBORDINATE));

    piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));

    piradip_tb_axilite_manager manager(.name("AXI MANAGER"), .aximm(axilite.MANAGER));

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

        manager.read('h1C, data);
        manager.read('h1C, data);
        manager.read('h1C, data);
        manager.read('h1C, data);

        clk_gen.sleep(40);

        $finish;
    end


endmodule
