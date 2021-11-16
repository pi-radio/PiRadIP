package piradip_axi4;

    localparam AXI_RESP_OKAY    = 2'b00;
    localparam AXI_RESP_EXOKAY  = 2'b01;
    localparam AXI_RESP_SLVERR  = 2'b10;
    localparam AXI_RESP_DECERR  = 2'b11;
    
    localparam AXI_BURST_FIXED  = 2'b00;
    localparam AXI_BURST_INCR   = 2'b01;
    localparam AXI_BURST_WRAP   = 2'b10;
    localparam AXI_BURST_RSRVD  = 2'b11;
    
    localparam AXI_SIZE_1       = 3'b000;
    localparam AXI_SIZE_2       = 3'b001;
    localparam AXI_SIZE_4       = 3'b010;
    localparam AXI_SIZE_8       = 3'b011;
    localparam AXI_SIZE_16      = 3'b100;
    localparam AXI_SIZE_32      = 3'b101;
    localparam AXI_SIZE_64      = 3'b110;
    localparam AXI_SIZE_128     = 3'b111;
    
    localparam AXI_LOCK_NORMAL    = 1'b0;
    localparam AXI_LOCK_EXCLUSIVE = 1'b1;

    localparam AXI_CACHE_DEVICE_NON_BUFFERABLE                = 4'b0000;
    localparam AXI_CACHE_DEVICE_BUFFERABLE                    = 4'b0001;
    localparam AXI_CACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE  = 4'b0010;
    localparam AXI_CACHE_NORMAL_NON_CACHEABLE                 = 4'b0011;

    localparam AXI_ARCACHE_WRITE_THROUGH_NO_ALLOCATE            = 4'b1010;
    localparam AXI_ARCACHE_WRITE_THROUGH_READ_ALLOCATE          = 4'b1110;
    localparam AXI3_ARCACHE_WRITE_THROUGH_READ_ALLOCATE         = 4'b0110;
    localparam AXI_ARCACHE_WRITE_THROUGH_WRITE_ALLOCATE         = 4'b1010;
    localparam AXI_ARCACHE_WRITE_THROUGH_BOTH_ALLOCATE          = 4'b1110;
    localparam AXI_ARCACHE_WRITE_BACK_NO_ALLOCATE               = 4'b1011;
    localparam AXI_ARCACHE_WRITE_BACK_READ_ALLOCATE             = 4'b1111;
    localparam AXI3_ARCACHE_WRITE_BACK_READ_ALLOCATE            = 4'b0111;
    localparam AXI_ARCACHE_WRITE_BACK_WRITE_ALLOCATE            = 4'b1011;
    localparam AXI_ARCACHE_WRITE_BACK_BOTH_ALLOCATE             = 4'b1111;

    localparam AXI_AWCACHE_WRITE_THROUGH_NO_ALLOCATE            = 4'b0110;
    localparam AXI_AWCACHE_WRITE_THROUGH_READ_ALLOCATE          = 4'b0110;
    localparam AXI_AWCACHE_WRITE_THROUGH_WRITE_ALLOCATE         = 4'b1110;
    localparam AXI3_AWCACHE_WRITE_THROUGH_WRITE_ALLOCATE        = 4'b1010;
    localparam AXI_AWCACHE_WRITE_THROUGH_BOTH_ALLOCATE          = 4'b1110;
    localparam AXI_AWCACHE_WRITE_BACK_NO_ALLOCATE               = 4'b0111;
    localparam AXI_AWCACHE_WRITE_BACK_READ_ALLOCATE             = 4'b0111;
    localparam AXI_AWCACHE_WRITE_BACK_WRITE_ALLOCATE            = 4'b1111;
    localparam AXI3_AWCACHE_WRITE_BACK_WRITE_ALLOCATE           = 4'b1011;
    localparam AXI_AWCACHE_WRITE_BACK_BOTH_ALLOCATE             = 4'b1111;

    localparam AXI_PROT_PRIVELEGED  = 3'b001;
    localparam AXI_PROT_NONSECURE   = 3'b010;
    localparam AXI_PROT_DATA        = 3'b000;
    localparam AXI_PROT_INSTRUCTION = 3'b100;
    
    
    localparam AXI_QOS_DEFAULT    = 4'b0000;

    localparam AXI_REGION_DEFAULT = 4'b0000;
    
    typedef logic [1:0] axi_resp_t;
    typedef logic [1:0] axi_burst_t;
    typedef logic [2:0] axi_size_t;
    typedef logic [7:0] axi_len_t;
endpackage

`define PIRADIP_PREFIX_ASSIGN(x, prefix)  .x(prefix``x)
`define PIRADIP_PREFIX_ALWAYS_COMB_OUT(ifname, x, prefix)  always_comb prefix``x=ifname.x
`define PIRADIP_PREFIX_ALWAYS_COMB_IN(ifname, x, prefix)  always_comb ifname.x=prefix``x
`define PIRADIP_PREFIX_ASSIGN_OUT(ifname, x, prefix)  assign prefix``x=ifname.x
`define PIRADIP_PREFIX_ASSIGN_IN(ifname, x, prefix)  assign ifname.x=prefix``x

`define PIRADIP_AXI4_MANAGER_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ID_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(AWUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ARUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(WUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(RUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(BUSER_WIDTH, xil_prefix_const)  \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    /* Write Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awready, xil_prefix); \
    /* Write Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wready, xil_prefix); \
    /* Write Response Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, buser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bready, xil_prefix); \
    /* Read Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, aruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arready, xil_prefix); \
    /* Read Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, ruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rready, xil_prefix);

`define PIRADIP_AXI4_SUBORDINATE_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ID_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(AWUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(ARUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(WUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(RUSER_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(BUSER_WIDTH, xil_prefix_const)  \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    /* Write Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awready, xil_prefix); \
    /* Write Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wuser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wready, xil_prefix); \
    /* Write Response Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, buser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bready, xil_prefix); \
    /* Read Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arlen, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arsize, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arburst, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arlock, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arcache, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arqos, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, aruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arready, xil_prefix); \
    /* Read Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rlast, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, ruser, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rready, xil_prefix);
    
`define PIRADIP_AXI4LITE_MANAGER_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm_lite #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const) \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    /* Write Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awready, xil_prefix); \
    /* Write Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wready, xil_prefix); \
    /* Write Response Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bready, xil_prefix); \
    /* Read Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arready, xil_prefix); \
    /* Read Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rready, xil_prefix);
    
`define PIRADIP_AXI4LITE_SUBORDINATE_ADAPTER(ifname, xil_prefix_const, xil_prefix) \
    axi4mm_lite #( \
        `PIRADIP_PREFIX_ASSIGN(ADDR_WIDTH, xil_prefix_const), \
        `PIRADIP_PREFIX_ASSIGN(DATA_WIDTH, xil_prefix_const) \
    ) ifname ( \
        `PIRADIP_PREFIX_ASSIGN(clk, xil_prefix``a), \
        `PIRADIP_PREFIX_ASSIGN(resetn, xil_prefix``a) \
    ); \
    /* Write Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awaddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, awvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, awready, xil_prefix); \
    /* Write Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wstrb, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, wvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, wready, xil_prefix); \
    /* Write Response Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, bvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, bready, xil_prefix); \
    /* Read Address Bus */ \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, araddr, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arprot, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, arvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, arready, xil_prefix); \
    /* Read Data Bus */ \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rdata, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rresp, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_OUT(ifname, rvalid, xil_prefix); \
    `PIRADIP_PREFIX_ASSIGN_IN(ifname, rready, xil_prefix);        
        