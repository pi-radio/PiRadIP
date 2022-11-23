`timescale 1ns / 1ps

`include "piradip_axi4.svh"



interface axi4mm #(
    parameter integer ADDR_WIDTH = 32,
    parameter integer DATA_WIDTH = 32,
    parameter integer ID_WIDTH = 1,
    parameter integer AWUSER_WIDTH = 0,
    parameter integer ARUSER_WIDTH = 0,
    parameter integer WUSER_WIDTH = 0,
    parameter integer RUSER_WIDTH = 0,
    parameter integer BUSER_WIDTH = 0
) (
    input logic clk,
    input logic resetn
);
  import piradip_axi4::*;

  typedef logic [ID_WIDTH-1:0] id_t;
  typedef logic [DATA_WIDTH-1:0] data_t;
  typedef logic [DATA_WIDTH/8-1:0] strb_t;
  typedef logic [ADDR_WIDTH-1:0] addr_t;
  typedef logic [ARUSER_WIDTH-1:0] aruser_t;
  typedef logic [RUSER_WIDTH-1:0] ruser_t;
  typedef logic [AWUSER_WIDTH-1:0] awuser_t;
  typedef logic [WUSER_WIDTH-1:0] wuser_t;
  typedef logic [BUSER_WIDTH-1:0] buser_t;

  logic aclk;
  logic aresetn;
  id_t awid;
  addr_t awaddr;
  axi_len_t awlen;
  axi_size_t awsize;
  axi_burst_t awburst;
  logic awlock;
  axi_cache_t awcache;
  axi_prot_t awprot;
  axi_qos_t awqos;
  axi_region_t awregion;
  awuser_t awuser;
  logic awvalid;
  logic awready;
  data_t wdata;
  strb_t wstrb;
  logic wlast;
  wuser_t wuser;
  logic wvalid;
  logic wready;
  id_t bid;
  axi_resp_t bresp;
  buser_t buser;
  logic bvalid;
  logic bready;
  id_t arid;
  addr_t araddr;
  axi_len_t arlen;
  axi_size_t arsize;
  axi_burst_t arburst;
  logic arlock;
  axi_cache_t arcache;
  axi_prot_t arprot;
  axi_qos_t arqos;
  axi_region_t arregion;
  aruser_t aruser;
  logic arvalid;
  logic arready;
  id_t rid;
  data_t rdata;
  axi_resp_t rresp;
  logic rlast;
  ruser_t ruser;
  logic rvalid;
  logic rready;

  assign aclk = clk;
  assign aresetn = resetn;

  function integer data_width();
    data_width = DATA_WIDTH;
  endfunction

  function integer addr_width();
    addr_width = ADDR_WIDTH;
  endfunction
   
  modport MANAGER(
      import data_width,
      import addr_width,
      output 
	     awid, awaddr, awlen, awsize, awburst, awlock, awcache, awprot, awqos, awregion, awuser, awvalid,
	     wdata, wstrb, wlast, wuser, wvalid,
	     bready,
	     arid, araddr, arlen, arsize, arburst, arlock, arcache, arprot, arqos, arregion, aruser, arvalid,
	     rready,
      input  aclk, aresetn,
	     awready,
	     wready,
	     bid, bresp, buser, bvalid,
	     arready,
	     rid, rdata, rresp, rlast, ruser, rvalid
  );

  modport SUBORDINATE(
      import data_width,
      import addr_width,
      output
            awready,
            wready,
            bid, bresp, buser, bvalid,
            arready,
            rid, rdata, rresp, rlast, ruser, rvalid,
      input aclk, aresetn,
            awid, awaddr, awlen, awsize, awburst, awlock, awcache, awprot, awqos, awregion, awuser, awvalid,
            wdata, wstrb, wlast, wuser, wvalid,
            bready,
            arid, araddr, arlen, arsize, arburst, arlock, arcache, arprot, arqos, arregion, aruser, arvalid,
            rready
  );


endinterface

module piradip_axi4_imp #(
    parameter integer DATA_WIDTH = 32,
    parameter integer ADDR_WIDTH = 10
) (
    axi4mm aximm
);

  import piradip_axi4::*;

  localparam integer ADDR_LSB = (DATA_WIDTH / 32) + 1;
  localparam integer OPT_MEM_ADDR_BITS = 7;
  localparam integer USER_NUM_MEM = 1;


  assign aximm.bid = aximm.awid;
  assign aximm.rid = aximm.arid;

  reg [ADDR_WIDTH-1 : 0] cur_awaddr;
  reg [ADDR_WIDTH-1 : 0] cur_araddr;
  wire aw_wrap_en;
  wire ar_wrap_en;
  wire [31:0] aw_wrap_size;
  wire [31:0] ar_wrap_size;
  reg cur_awv_awr_flag;
  reg cur_arv_arr_flag;
  reg [7:0] cur_awlen_cntr;
  reg [7:0] cur_arlen_cntr;
  reg [1:0] cur_arburst;
  reg [1:0] cur_awburst;
  reg [7:0] cur_arlen;
  reg [7:0] cur_awlen;
  wire [OPT_MEM_ADDR_BITS:0] mem_address;
  wire [USER_NUM_MEM-1:0] mem_select;
  reg [DATA_WIDTH-1:0] mem_data_out[0 : USER_NUM_MEM-1];

  genvar i;
  genvar j;
  genvar mem_byte_index;

  assign aw_wrap_size = (DATA_WIDTH / 8 * (cur_awlen));
  assign ar_wrap_size = (DATA_WIDTH / 8 * (cur_arlen));
  assign aw_wrap_en   = ((cur_awaddr & aw_wrap_size) == aw_wrap_size) ? 1'b1 : 1'b0;
  assign ar_wrap_en   = ((cur_araddr & ar_wrap_size) == ar_wrap_size) ? 1'b1 : 1'b0;

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.awready <= 1'b0;
      cur_awv_awr_flag <= 1'b0;
    end else if (~aximm.awready && aximm.awvalid && ~cur_awv_awr_flag && ~cur_arv_arr_flag) begin
      aximm.awready <= 1'b1;
      cur_awv_awr_flag <= 1'b1;
    end else if (aximm.wlast && aximm.wready) begin
      cur_awv_awr_flag <= 1'b0;
    end else begin
      aximm.awready <= 1'b0;
    end
  end

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      cur_awaddr <= 0;
      cur_awlen_cntr <= 0;
      cur_awburst <= 0;
      cur_awlen <= 0;
    end else if (~aximm.awready && aximm.awvalid && ~cur_awv_awr_flag) begin
      // address latching
      cur_awaddr <= aximm.awaddr[ADDR_WIDTH-1:0];
      cur_awburst <= aximm.awburst;
      cur_awlen <= aximm.awlen;
      // start address of transfer
      cur_awlen_cntr <= 0;
    end else if ((cur_awlen_cntr <= cur_awlen) && aximm.wready && aximm.wvalid) begin
      cur_awlen_cntr <= cur_awlen_cntr + 1;

      case (cur_awburst)
        AXI_BURST_FIXED: cur_awaddr <= cur_awaddr;
        AXI_BURST_INCR:  cur_awaddr <= {cur_awaddr[ADDR_WIDTH-1:ADDR_LSB] + 1, {{ADDR_LSB} {1'b0}}};
        AXI_BURST_WRAP:
        if (aw_wrap_en) begin
          cur_awaddr <= (cur_awaddr - aw_wrap_size);
        end else begin
          cur_awaddr[ADDR_WIDTH-1:ADDR_LSB] <= cur_awaddr[ADDR_WIDTH-1:ADDR_LSB] + 1;
          cur_awaddr[ADDR_LSB-1:0] <= {ADDR_LSB{1'b0}};
        end
        default: begin
        end
      endcase
    end
  end

  // Implement aximm.wready ADDR_LSB
  // aximm.wready is asserted for one aximm.aclk clock cycle when both
  // aximm.awvalid and aximm.wvalid are asserted. aximm.wready is
  // de-asserted when reset is low.
  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.wready <= 1'b0;
    end else if (~aximm.wready && aximm.wvalid && cur_awv_awr_flag) begin
      aximm.wready <= 1'b1;
    end else if (aximm.wlast && aximm.wready) begin
      aximm.wready <= 1'b0;
    end
  end


  // Implement write response logic ADDR_LSB

  // The write response and response valid signals are asserted by the slave
  // when aximm.wready, aximm.wvalid, aximm.wready and aximm.wvalid are asserted.
  // This marks the acceptance of address and indicates the status of
  // write transaction.

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.bvalid <= 0;
      aximm.bresp  <= AXI_RESP_OKAY;
      aximm.buser  <= 0;
    end else if (cur_awv_awr_flag && aximm.wready && aximm.wvalid && ~aximm.bvalid && aximm.wlast) begin
      aximm.bvalid <= 1'b1;
      aximm.bresp  <= AXI_RESP_OKAY;
    end else if (aximm.bready && aximm.bvalid) begin
      aximm.bvalid <= 1'b0;
    end
  end
  // Implement aximm.arready generation

  // aximm.arready is asserted for one aximm.aclk clock cycle when
  // aximm.arvalid is asserted. aximm.awready is
  // de-asserted when reset (active low) is asserted.
  // The read address is also latched when aximm.arvalid is
  // asserted. cur_araddr is reset to zero on reset assertion.

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.arready <= 1'b0;
      cur_arv_arr_flag <= 1'b0;
    end else if (~aximm.arready && aximm.arvalid && ~cur_awv_awr_flag && ~cur_arv_arr_flag) begin
      aximm.arready <= 1'b1;
      cur_arv_arr_flag <= 1'b1;
    end else if (aximm.rvalid && aximm.rready && cur_arlen_cntr == cur_arlen) begin
      cur_arv_arr_flag <= 1'b0;
    end else begin
      aximm.arready <= 1'b0;
    end
  end
  // Implement cur_araddr latching

  //This process is used to latch the address when both
  //aximm.arvalid and aximm.rvalid are valid.
  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      cur_araddr <= 0;
      cur_arlen_cntr <= 0;
      cur_arburst <= 0;
      cur_arlen <= 0;
      aximm.rlast <= 1'b0;
      aximm.ruser <= 0;
    end else if (~aximm.arready && aximm.arvalid && ~cur_arv_arr_flag) begin
      // address latching
      cur_araddr <= aximm.araddr[ADDR_WIDTH-1:0];
      cur_arburst <= aximm.arburst;
      cur_arlen <= aximm.arlen;
      // start address of transfer
      cur_arlen_cntr <= 0;
      aximm.rlast <= 1'b0;
    end else if ((cur_arlen_cntr <= cur_arlen) && aximm.rvalid && aximm.rready) begin
      cur_arlen_cntr <= cur_arlen_cntr + 1;
      aximm.rlast <= 1'b0;
      case (cur_arburst)
        AXI_BURST_FIXED: cur_araddr <= cur_araddr;
        AXI_BURST_INCR: cur_araddr <= {cur_araddr[ADDR_WIDTH-1:ADDR_LSB] + 1, {ADDR_LSB{1'b0}}};
        AXI_BURST_WRAP:
        cur_araddr <= ar_wrap_en ? (cur_araddr - ar_wrap_size) : { cur_araddr[ADDR_WIDTH - 1:ADDR_LSB] + 1, {ADDR_LSB{1'b0}}};
        default: begin
        end
      endcase
    end else if ((cur_arlen_cntr == cur_arlen) && ~aximm.rlast && cur_arv_arr_flag) begin
      aximm.rlast <= 1'b1;
    end else if (aximm.rready) begin
      aximm.rlast <= 1'b0;
    end
  end

  // Implement cur_arvalid generation

  // aximm.rvalid is asserted for one aximm.aclk clock cycle when both
  // aximm.arvalid and aximm.arready are asserted. The slave registers
  // data are available on the aximm.rdata bus at this instance. The
  // assertion of aximm.rvalid marks the validity of read data on the
  // bus and aximm.rresp indicates the status of read transaction.aximm.rvalid
  // is deasserted on reset (active low). aximm.rresp and aximm.rdata are
  // cleared to zero on reset (active low).

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.rvalid <= 0;
      aximm.rresp  <= AXI_RESP_OKAY;
    end else if (cur_arv_arr_flag && ~aximm.rvalid) begin
      aximm.rvalid <= 1'b1;
      aximm.rresp  <= AXI_RESP_OKAY;
      // 'OKAY' ADDR_LSB
    end else if (aximm.rvalid && aximm.rready) begin
      aximm.rvalid <= 1'b0;
    end
  end


  /*
// ------------------------------------------
  // -- Example code to access user logic memory region
  // ------------------------------------------

  generate
    if (user_NUM_MEM >= 1)
      begin
        assign mem_select  = 1;
        assign mem_address = (cur_arv_arr_flag? cur_araddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB]:(cur_awv_awr_flag? cur_awaddr[ADDR_LSB+OPT_MEM_ADDR_BITS:ADDR_LSB]:0));
      end
  endgenerate

  // implement Block RAM(s)
  generate
    for(i=0; i<= user_NUM_MEM-1; i=i+1)
      begin:BRAM_GEN
        wire mem_rden;
        wire mem_wren;

        assign mem_wren = aximm.wready && aximm.wvalid ;

        assign mem_rden = cur_arv_arr_flag ; //& ~aximm.rvalid

        for(mem_byte_index=0; mem_byte_index<= (DATA_WIDTH/8-1); mem_byte_index=mem_byte_index+1)
        begin:BYTE_BRAM_GEN
          wire [8-1:0] data_in ;
          wire [8-1:0] data_out;
          reg  [8-1:0] byte_ram [0 : 255];
          integer  j;

          //assigning 8 bit data
          assign data_in  = aximm.wDATA[(mem_byte_index*8+7) -: 8];
          assign data_out = byte_ram[mem_address];

          always @(posedge aximm.aclk)
          begin
            if (mem_wren && aximm.wSTRB[mem_byte_index])
              begin
                byte_ram[mem_address] <= data_in;
              end
          end

          always @(posedge aximm.aclk)
          begin
            if (mem_rden)
              begin
                mem_data_out[i][(mem_byte_index*8+7) -: 8] <= data_out;
              end
          end

      end
    end
  endgenerate
  //Output register or memory read data

  always @( mem_data_out, aximm.rvalid)
  begin
    if (aximm.rvalid)
      begin
        // Read address mux
        aximm.rdata <= mem_data_out[0];
      end
    else
      begin
        aximm.rdata <= 32'h00000000;
      end
  end

  // Add user logic here

  // User logic ends
*/
endmodule
