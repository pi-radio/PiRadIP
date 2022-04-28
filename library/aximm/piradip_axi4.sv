`timescale 1ns / 1ps

package piradip_axi4;
  localparam AXI_RESP_OKAY = 2'b00;
  localparam AXI_RESP_EXOKAY = 2'b01;
  localparam AXI_RESP_SLVERR = 2'b10;
  localparam AXI_RESP_DECERR = 2'b11;

  localparam AXI_BURST_FIXED = 2'b00;
  localparam AXI_BURST_INCR = 2'b01;
  localparam AXI_BURST_WRAP = 2'b10;
  localparam AXI_BURST_RSRVD = 2'b11;

  /* Burst size in bytes */
  localparam AXI_SIZE_1 = 3'b000;
  localparam AXI_SIZE_2 = 3'b001;
  localparam AXI_SIZE_4 = 3'b010;
  localparam AXI_SIZE_8 = 3'b011;
  localparam AXI_SIZE_16 = 3'b100;
  localparam AXI_SIZE_32 = 3'b101;
  localparam AXI_SIZE_64 = 3'b110;
  localparam AXI_SIZE_128 = 3'b111;

  localparam AXI_LOCK_NORMAL = 1'b0;
  localparam AXI_LOCK_EXCLUSIVE = 1'b1;

  localparam AXI_CACHE_DEVICE_NON_BUFFERABLE = 4'b0000;
  localparam AXI_CACHE_DEVICE_BUFFERABLE = 4'b0001;
  localparam AXI_CACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE = 4'b0010;
  localparam AXI_CACHE_NORMAL_NON_CACHEABLE = 4'b0011;

  localparam AXI_ARCACHE_WRITE_THROUGH_NO_ALLOCATE = 4'b1010;
  localparam AXI_ARCACHE_WRITE_THROUGH_READ_ALLOCATE = 4'b1110;
  localparam AXI3_ARCACHE_WRITE_THROUGH_READ_ALLOCATE = 4'b0110;
  localparam AXI_ARCACHE_WRITE_THROUGH_WRITE_ALLOCATE = 4'b1010;
  localparam AXI_ARCACHE_WRITE_THROUGH_BOTH_ALLOCATE = 4'b1110;
  localparam AXI_ARCACHE_WRITE_BACK_NO_ALLOCATE = 4'b1011;
  localparam AXI_ARCACHE_WRITE_BACK_READ_ALLOCATE = 4'b1111;
  localparam AXI3_ARCACHE_WRITE_BACK_READ_ALLOCATE = 4'b0111;
  localparam AXI_ARCACHE_WRITE_BACK_WRITE_ALLOCATE = 4'b1011;
  localparam AXI_ARCACHE_WRITE_BACK_BOTH_ALLOCATE = 4'b1111;

  localparam AXI_AWCACHE_WRITE_THROUGH_NO_ALLOCATE = 4'b0110;
  localparam AXI_AWCACHE_WRITE_THROUGH_READ_ALLOCATE = 4'b0110;
  localparam AXI_AWCACHE_WRITE_THROUGH_WRITE_ALLOCATE = 4'b1110;
  localparam AXI3_AWCACHE_WRITE_THROUGH_WRITE_ALLOCATE = 4'b1010;
  localparam AXI_AWCACHE_WRITE_THROUGH_BOTH_ALLOCATE = 4'b1110;
  localparam AXI_AWCACHE_WRITE_BACK_NO_ALLOCATE = 4'b0111;
  localparam AXI_AWCACHE_WRITE_BACK_READ_ALLOCATE = 4'b0111;
  localparam AXI_AWCACHE_WRITE_BACK_WRITE_ALLOCATE = 4'b1111;
  localparam AXI3_AWCACHE_WRITE_BACK_WRITE_ALLOCATE = 4'b1011;
  localparam AXI_AWCACHE_WRITE_BACK_BOTH_ALLOCATE = 4'b1111;

  localparam AXI_PROT_PRIVELEGED = 3'b001;
  localparam AXI_PROT_NONSECURE = 3'b010;
  localparam AXI_PROT_DATA = 3'b000;
  localparam AXI_PROT_INSTRUCTION = 3'b100;


  localparam AXI_QOS_DEFAULT = 4'b0000;

  localparam AXI_REGION_DEFAULT = 4'b0000;

  typedef logic [1:0] axi_resp_t;
  typedef logic [1:0] axi_burst_t;
  typedef logic [2:0] axi_size_t;
  typedef logic [7:0] axi_len_t;
  typedef logic [2:0] axi_prot_t;
  typedef logic [3:0] axi_cache_t;
  typedef logic [3:0] axi_qos_t;
  typedef logic [3:0] axi_region_t;
  typedef logic axi_lock_t;
endpackage
