

module vsn_open(vsn_port.U p);
  always_comb p.b = p.a;
endmodule

module vsn_terminator(vsn_port.U p);
  always_comb p.b = 0;
endmodule // vsn_terminator


module vsn_test1();
  
  localparam STREAM_WIDTH=256;
  localparam NRFDC = 2;
  
  logic mem_clk;
  logic mem_rstn;

  logic [NRFDC-1:0] stream_clk;
  logic [NRFDC-1:0] stream_rstn;

  logic [NRFDC-1:0] adc_clk;

  
  logic signed [15:0] cur_adc_sample[NRFDC-1:0];
  logic signed [15:0] cur_dac_sample[NRFDC-1:0];

  
  piradip_tb_clkgen mm_clk_gen(.clk(mem_clk));
  
  //axi4mm_lite ctrl(.clk(mem_clk), .resetn(mem_rstn));
  //piradip_tb_axilite_manager control_manager(.aximm(ctrl));

  
  axi4s #(.WIDTH(256)) stream_in[NRFDC-1:0](.clk(stream_clk), .resetn(stream_rstn));
  axi4s #(.WIDTH(256)) stream_out[NRFDC-1:0](.clk(stream_clk), .resetn(stream_rstn));

  logic vsn_clk, vsn_rstn;

  always_comb vsn_clk = stream_clk[0];
  always_comb vsn_rstn = stream_rstn[0];
  
  genvar n;

  vsn_connection extcon[NRFDC]();
  
  REAL_ADC adc0(.adc_out(stream_in[0]),
    .adc_clk(adc_clk[0]),
    .axis_clk(stream_clk[0]),
    .cur_sample(cur_adc_sample[0]));

  REAL_ADC adc1(.adc_out(stream_in[1]),
    .adc_clk(adc_clk[1]),
    .axis_clk(stream_clk[1]),
    .cur_sample(cur_adc_sample[1]));


  generate
    for(n = 0; n < NRFDC; n++) begin
      REAL_DAC dac[NRFDC-1:0](.dac_in(stream_out[n]),
      .dac_clk(adc_clk[n]),
      .axis_clk(stream_clk[n]),
      .cur_sample(cur_dac_sample[n]));
      
      vsn_rfdc_adapter rfdc_adapter(
      .vsn_clk(vsn_clk),
      .vsn_rstn(vsn_rstn),
      .vsn(extcon[n].P[0]),
      .axis_a(stream_in[n].SUBORDINATE),
      .axis_b(stream_out[n].MANAGER)
	);
    end
  endgenerate
  
  
  integer N;
  integer i, j;

  localparam N_SAMPLES=16;
  localparam SAMPLE_WIDTH=16;
  localparam PI =  3.1415926535897;

  logic [17:0] passthru[2][2];

  always_comb begin
    passthru[0][0] = 0;
    passthru[0][1] = 18'h10000;

    passthru[1][0] = 18'h10000;
    passthru[1][1] = 0;
  end

  vsn_connection conn[2]();

  vsn_sparam_2port two_port (
    .vsn_clk(vsn_clk),
    .vsn_rstn(vsn_rstn),
    .p0(extcon[0].P[1]),
    .p1(extcon[1].P[1]),
    .S(passthru)
    );
  
/*  
  logic [17:0] wilkinson[3][3];

  always_comb begin
    wilkinson[0][0] = 0;
    wilkinson[0][1] = 18'hB504;
    wilkinson[0][2] = 18'hB504;

    wilkinson[1][0] = 18'hB504;
    wilkinson[1][1] = 0;
    wilkinson[1][2] = 0;

    wilkinson[2][0] = 18'hB504;
    wilkinson[2][1] = 0;
    wilkinson[2][2] = 0;    
  end // always_comb

  vsn_connection conn0(.S0(p0.U),
    .S1(p1.U));
  
  vsn_connection conn1(.S0(p2.U),
    .S1(p3.U));

  vsn_connection conn2(.S0(p4.U),
    .S1(p5.U));

  
  vsn_terminator term(.p(p0.U));
    
  vsn_open open(.p(p5.U));
  
  vsn_sparam_3port node1(
    .vsn_clk(vsn_clk),
    .vsn_rstn(vsn_rstn),
    .p0(p1.U),
    .p1(extport[0].U),
    .p2(p2.U),
    .S(wilkinson));
  
  vsn_sparam_3port node2(
    .vsn_clk(vsn_clk),
    .vsn_rstn(vsn_rstn),
    .p0(p3.U),
    .p1(extport[1].U),
    .p2(p4.U),
    .S(wilkinson));
*/  
    
    
  initial
    begin      
      mem_rstn <= 0;
      stream_rstn[0] <= 0;      
      stream_rstn[1] <= 0;      
      
      mm_clk_gen.sleep(5);

      @(posedge stream_clk[0]) stream_rstn[0] <= 1;
      @(posedge stream_clk[0]) stream_rstn[1] <= 1;
      @(posedge mem_clk) mem_rstn <= 1;

      mm_clk_gen.sleep(20);

      for (i = 0; i < 16*32; i++) begin
	adc0.add_sample(32767 * $sin(i * 2 * PI/19));
	adc1.add_sample(32767 * $sin(i * 2 * PI/16));
      end

      adc0.drain();
      adc1.drain();
      mm_clk_gen.sleep(5);
      
    end
endmodule
