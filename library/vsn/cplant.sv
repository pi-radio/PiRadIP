module vsn_cable_plant_1(
  axi4s.SUBORDINATE adc0,
  axi4s.MANAGER dac0,

  axi4s.SUBORDINATE adc1,
  axi4s.MANAGER dac1,

  axi4s.SUBORDINATE adc2,
  axi4s.MANAGER dac2,

  axi4s.SUBORDINATE adc3,
  axi4s.MANAGER dac3,

  axi4s.SUBORDINATE adc4,
  axi4s.MANAGER dac4,

  axi4s.SUBORDINATE adc5,
  axi4s.MANAGER dac5,

  axi4s.SUBORDINATE adc6,
  axi4s.MANAGER dac6,

  axi4s.SUBORDINATE adc7,
  axi4s.MANAGER dac7);

  vsn_port phys_port0;
  vsn_port phys_port1;
  vsn_port phys_port2;
  vsn_port phys_port3;
  vsn_port phys_port4;
  vsn_port phys_port5;
  vsn_port phys_port6;
  vsn_port phys_port7;

  always_comb phys_port0.a = dac0.tdata; 
  always_comb adc0.tdata = phys_port0.b; 
  
endmodule
