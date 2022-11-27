`timescale 1ns / 1ps

module piradip_axi4_ram_adapter #(
    parameter integer DATA_WIDTH = 32,
    parameter integer ADDR_WIDTH = 10,
    parameter integer WE_WIDTH = 1,
    parameter integer READ_LATENCY = 1
) (
    axi4mm aximm,
    piradip_ram_if.CLIENT mem
);

  import piradip_axi4::*;

  localparam integer ADDR_LSB = (DATA_WIDTH / 32) + 1;

  typedef enum {
    IDLE  = 0,
    READ,
    WRITE
  } mem_if_state_t;

  mem_if_state_t mem_if_state;

  assign aximm.bid = aximm.awid;
  assign aximm.rid = aximm.arid;

  wire aw_wrap_en;
  wire ar_wrap_en;
  wire [31:0] aw_wrap_size;
  wire [31:0] ar_wrap_size;
  reg write_v_awr_flag;
  reg read_v_arr_flag;
  reg [7:0] write_len_cntr;
  reg [7:0] read_len_cntr;

  logic unit_ready;


  genvar i;
  genvar j;
  genvar mem_byte_index;



  assign mem.wdata = aximm.wdata;

  typedef logic [ADDR_WIDTH-1 : 0] axi_addr_t;

  logic write_cmd_valid;
  axi_addr_t write_addr;
  axi_burst_t write_burst;
  axi_len_t write_len;
  logic [$bits(aximm.awid)-1:0] write_id;
  axi_size_t write_size;
  axi_lock_t write_lock;
  axi_cache_t write_cache;
  axi_qos_t write_qos;
  axi_region_t write_region;
  logic [$bits(aximm.awuser)-1:0] write_user;

  logic read_cmd_valid;
  axi_addr_t read_addr;
  axi_burst_t read_burst;
  axi_len_t read_len;
  axi_size_t read_size;
  axi_lock_t read_lock;
  axi_cache_t read_cache;
  axi_prot_t read_prot;
  axi_qos_t read_qos;
  axi_region_t read_region;
  logic [$bits(aximm.aruser)-1:0] read_user;

  logic last_write_cycle;

  logic pending_write, pending_read;

  assign aw_wrap_size = (DATA_WIDTH / 8 * (write_len));
  assign ar_wrap_size = (DATA_WIDTH / 8 * (read_len));
  assign aw_wrap_en = ((write_addr & aw_wrap_size) == aw_wrap_size) ? 1'b1 : 1'b0;
  assign ar_wrap_en = ((read_addr & ar_wrap_size) == ar_wrap_size) ? 1'b1 : 1'b0;

  assign mem.addr = (mem_if_state == READ) ? read_addr[ADDR_WIDTH - 1:ADDR_LSB] :
        (mem_if_state == WRITE) ? write_addr[ADDR_WIDTH - 1:ADDR_LSB] :
        0;

  assign mem.we = aximm.wready & aximm.wvalid;

  /*** WRITE LOGIC ***/
  assign last_write_cycle = ((write_len_cntr + 1) == write_len);

  assign aximm.awready = unit_ready & ~write_cmd_valid;
  assign aximm.wready = (mem_if_state == WRITE);


  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      write_cmd_valid <= 1'b0;
    end else if (~write_cmd_valid & aximm.awvalid) begin
      write_cmd_valid <= 1'b1;
    end else if (aximm.wlast) begin
      write_cmd_valid <= 1'b0;
    end else begin
      write_cmd_valid <= write_cmd_valid;
    end
  end

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      write_addr  <= 0;
      write_burst <= 0;
      write_len   <= 0;
    end else if (aximm.awready & aximm.awvalid) begin
      write_len_cntr <= 0;
      write_addr <= aximm.awaddr;
      write_burst <= aximm.awburst;
      write_len <= aximm.awlen;
    end else if (aximm.wready & aximm.wvalid) begin
      write_len_cntr <= write_len_cntr + 1;

      case (write_burst)
        AXI_BURST_FIXED: write_addr <= write_addr;
        AXI_BURST_INCR:  write_addr <= {write_addr[ADDR_WIDTH-1:ADDR_LSB] + 1, {{ADDR_LSB} {1'b0}}};
        AXI_BURST_WRAP:
        if (aw_wrap_en) begin
          write_addr <= (write_addr - aw_wrap_size);
        end else begin
          write_addr[ADDR_WIDTH-1:ADDR_LSB] <= write_addr[ADDR_WIDTH-1:ADDR_LSB] + 1;
          write_addr[ADDR_LSB-1:0] <= {ADDR_LSB{1'b0}};
        end
        default: begin
        end
      endcase
    end
  end

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      aximm.bvalid <= 1'b0;
      aximm.bresp  <= AXI_RESP_SLVERR;
      aximm.buser  <= 0;
    end else if (aximm.wready & aximm.wvalid & aximm.wlast) begin
      aximm.bvalid <= 1'b1;
      aximm.bresp  <= AXI_RESP_OKAY;
      aximm.buser  <= 0;
    end else begin
      aximm.bvalid <= 1'b0;
      aximm.bresp  <= AXI_RESP_SLVERR;
      aximm.buser  <= 0;
    end
  end

  /*** READ LOGIC ***/

  always_comb aximm.arready = unit_ready & ~read_cmd_valid;
  logic rd_fifo_sleep, rd_fifo_rd_rst_busy, rd_fifo_wr_rst_busy;

  localparam STARTUP_CYCLES = 20;
  int startup_counter;

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn || rd_fifo_rd_rst_busy || rd_fifo_wr_rst_busy) begin
      unit_ready <= 1'b0;
      startup_counter <= STARTUP_CYCLES;
    end else if (startup_counter > 0) begin
      startup_counter <= startup_counter - 1;
    end else begin
      unit_ready <= 1'b1;
    end
  end


  logic rd_fifo_empty, rd_fifo_full;
  logic rd_fifo_prog_full;
  logic rd_fifo_rd_en, rd_fifo_wr_en;
  logic rd_fifo_tlast;
  logic read_active;
  logic last_ram_read;

  always_comb last_ram_read = (read_len_cntr == read_len);
  always_comb read_active   = (mem_if_state == READ) && ~rd_fifo_prog_full;
  always_comb rd_fifo_sleep = ~aximm.aresetn || rd_fifo_rd_rst_busy || rd_fifo_wr_rst_busy;

  generate
    if (READ_LATENCY > 1) begin
      logic [READ_LATENCY-1:0] last_latency_fifo;
      logic [READ_LATENCY-1:0] rd_fifo_wr_en_fifo;

      always @(posedge aximm.aclk)
        last_latency_fifo = ~aximm.aresetn ? 0 : { last_ram_read, last_latency_fifo[1+:READ_LATENCY-1] };
      always @(posedge aximm.aclk)
        rd_fifo_wr_en_fifo = ~aximm.aresetn ? 0 : { read_active, rd_fifo_wr_en_fifo[1+:READ_LATENCY-1] };

      assign rd_fifo_tlast = last_latency_fifo[0];
      assign rd_fifo_wr_en = aximm.aresetn & rd_fifo_wr_en_fifo[0];
    end else begin
      always @(posedge aximm.aclk) rd_fifo_tlast <= last_ram_read;
      always @(posedge aximm.aclk) rd_fifo_wr_en <= aximm.aresetn & read_active;
    end
  endgenerate

  localparam FIFO_DEPTH = 16;
  localparam PROG_FULL_DEPTH = (READ_LATENCY >= 3) ? FIFO_DEPTH - READ_LATENCY : FIFO_DEPTH - 3;

  piradip_sync_fifo #(
      .WIDTH(DATA_WIDTH + 1),
      .PROG_FULL_THRESH(PROG_FULL_DEPTH),
      .DEPTH(FIFO_DEPTH)
  ) gearbox (
      .clk(aximm.aclk),
      .rst(~aximm.aresetn),
      .re(rd_fifo_rd_en),
      .we(rd_fifo_wr_en),
      .rd_rst_busy(rd_fifo_rd_rst_busy),
      .wr_rst_busy(rd_fifo_wr_rst_busy),
      .sleep(rd_fifo_sleep),
      .din({rd_fifo_tlast, mem.rdata}),
      .dout({aximm.rlast, aximm.rdata}),
      .empty(rd_fifo_empty),
      .prog_full(rd_fifo_prog_full)
  );

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      read_cmd_valid <= 1'b0;
    end else if (~read_cmd_valid & aximm.arvalid) begin
      read_cmd_valid <= 1'b1;
    end else if (last_ram_read) begin
      read_cmd_valid <= 1'b0;
    end else begin
      read_cmd_valid <= read_cmd_valid;
    end
  end

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn || rd_fifo_rd_rst_busy) begin
      aximm.rvalid <= 1'b0;
    end else begin
      if (aximm.rvalid) begin
        aximm.rvalid <= aximm.rready ? rd_fifo_rd_en : 1'b1;
      end else begin
        aximm.rvalid <= rd_fifo_rd_en;
      end
    end
  end

  assign rd_fifo_rd_en = (aximm.rready | ~aximm.rvalid) & ~rd_fifo_empty;

  assign aximm.rresp   = AXI_RESP_OKAY;

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      read_len_cntr <= 0;
      read_addr <= 0;
      read_burst <= 0;
      read_len <= 0;
      read_size <= 0;
      read_lock <= 0;
      read_cache <= 0;
      read_prot <= 0;
      read_qos <= 0;
      read_region <= 0;
      read_user <= 0;
    end else if (~read_cmd_valid & aximm.arvalid) begin
      read_len_cntr <= 0;
      read_addr <= aximm.araddr;
      read_burst <= aximm.arburst;
      read_len <= aximm.arlen;
      read_size <= aximm.arsize;
      read_lock <= aximm.arlock;
      read_cache <= aximm.arcache;
      read_prot <= aximm.arprot;
      read_qos <= aximm.arqos;
      read_region <= aximm.arregion;
      read_user <= aximm.aruser;
    end else if (read_active) begin
      read_len_cntr <= read_len_cntr + 1;

      case (read_burst)
        AXI_BURST_FIXED: read_addr <= read_addr;
        AXI_BURST_INCR:  read_addr <= {read_addr[ADDR_WIDTH-1:ADDR_LSB] + 1, {{ADDR_LSB} {1'b0}}};
        AXI_BURST_WRAP:
        if (ar_wrap_en) begin
          read_addr <= (read_addr - ar_wrap_size);
        end else begin
          read_addr[ADDR_WIDTH-1:ADDR_LSB] <= read_addr[ADDR_WIDTH-1:ADDR_LSB] + 1;
          read_addr[ADDR_LSB-1:0] <= {ADDR_LSB{1'b0}};
        end
        default: begin
        end
      endcase
    end
  end

  /*** ARBITER ***/
  assign pending_write = (aximm.awready && aximm.awvalid) | write_cmd_valid;
  assign pending_read  = (aximm.arready && aximm.arvalid) | read_cmd_valid;

  always @(posedge aximm.aclk) begin
    if (~aximm.aresetn) begin
      mem_if_state <= IDLE;
    end else begin
      case (mem_if_state)
        IDLE: begin
          if (pending_write) begin
            mem_if_state <= WRITE;
          end else if (pending_read) begin
            mem_if_state <= READ;
          end else begin
            mem_if_state <= IDLE;
          end
        end
        READ: begin
          if (last_ram_read) mem_if_state <= pending_write ? WRITE : IDLE;
          else mem_if_state <= READ;
        end
        WRITE: begin
          if (aximm.wlast) mem_if_state <= pending_read ? READ : IDLE;
          else mem_if_state <= WRITE;
        end
      endcase
    end
  end
endmodule
