
module piradip_tb_trigger_unit();
   wire clk;
   reg  rstn;

   localparam SEL_WIDTH=5;




   piradip_tb_clkgen #(.HALF_PERIOD(10)) clk_gen(.clk(clk));

   axi4mm_lite axilite_bus(.clk(clk), .resetn(rstn));

   piradip_tb_axilite_manager manager(.aximm(axilite_bus));

   logic [31:0]          triggers;

   piradip_trigger_unit trigger_unit(.axilite(axilite_bus.SUBORDINATE),
                                     .triggers(triggers));

   initial
     begin
        integer               i;

        $timeformat(-9, 2, " ns", 0);

        rstn <= 0;

        clk_gen.sleep(5);

        rstn <= 1;

        clk_gen.sleep(5);

        for (i = 0; i < 32; i++) begin
           manager.write(4*(3+i), i);
        end

        manager.write(4 * 2,1);

        clk_gen.sleep(400);

        $finish;

     end


endmodule
