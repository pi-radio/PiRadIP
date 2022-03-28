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
        