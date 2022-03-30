package piradip_axi4;
    localparam AXI_RESP_OKAY    = 2'b00;
    localparam AXI_RESP_EXOKAY  = 2'b01;
    localparam AXI_RESP_SLVERR  = 2'b10;
    localparam AXI_RESP_DECERR  = 2'b11;
    
    localparam AXI_BURST_FIXED  = 2'b00;
    localparam AXI_BURST_INCR   = 2'b01;
    localparam AXI_BURST_WRAP   = 2'b10;
    localparam AXI_BURST_RSRVD  = 2'b11;
    
    /* Burst size in bytes */
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
    typedef logic [2:0] axi_prot_t;
    typedef logic [3:0] axi_cache_t;
    typedef logic [3:0] axi_qos_t;
    typedef logic [3:0] axi_region_t;
    typedef logic axi_lock_t;
endpackage

`define AXI4MM_REGISTER_ADDR_LSB(data_width) (((data_width)/32)+1)    
`define AXI4MM_REGISTER_ADDR_BITS(data_width, addr_width) ((addr_width)-AXI4MM_REGISTER_ADDR_LSB(data_width))

interface axi4mm_lite #(
    parameter integer ADDR_WIDTH=8,
    parameter integer DATA_WIDTH=32
)(
    input logic clk, 
    input logic resetn
);
    localparam STRB_WIDTH=(DATA_WIDTH/8);
    
    logic aclk;
    logic aresetn;
    logic [ADDR_WIDTH-1 : 0] awaddr;
    logic [2 : 0] awprot;
    logic awvalid;
    logic awready;
    logic [DATA_WIDTH-1 : 0] wdata;
    logic [STRB_WIDTH-1 : 0] wstrb;
    logic wvalid;
    logic wready;
    logic [1 : 0] bresp;
    logic bvalid;
    logic bready;
    logic [ADDR_WIDTH-1 : 0] araddr;
    logic [2 : 0] arprot;
    logic arvalid;
    logic arready;
    logic [DATA_WIDTH-1 : 0] rdata;
    logic [1 : 0] rresp;
    logic rvalid;
    logic rready;
    
    modport MANAGER(input awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid,
                    output awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready, aclk, aresetn);

    modport SUBORDINATE(output awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid, aclk, aresetn,
                        input awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready);

    assign aclk = clk;
    assign aresetn = resetn;
endinterface

interface piradip_register_if #(
        parameter integer DATA_WIDTH = 32,
        parameter integer REGISTER_ADDR_BITS = 8
    )(
        input aclk,
        input aresetn
    );

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;

    logic wren;
    regno_t wreg_no;
    logic [DATA_WIDTH-1:0] wreg_data;
    logic [(DATA_WIDTH/8)-1:0] wstrb;
    logic rden;
    regno_t rreg_no;
    logic [DATA_WIDTH-1:0] rreg_data;       

    modport CLIENT(output wren, wreg_no, wreg_data, wstrb, rden, rreg_no, input rreg_data);
    modport SERVER(input wren, wreg_no, wreg_data, wstrb, rden, rreg_no, output rreg_data);
    
    function automatic logic is_reg_read(input regno_t regno);
        return rden && rreg_no == regno;
    endfunction;

    function automatic logic is_reg_write(input regno_t regno);
        return wren && wreg_no == regno;
    endfunction;

    function automatic logic reg_update_bit(input regno_t regno, input integer bitno, input logic v);
        return (wren && wreg_no == regno && (wstrb[bitno/8] == 1)) ? wreg_data[bitno] : v;
    endfunction;

    function automatic logic is_reg_bit_set(input regno_t regno, input integer bitno);
        return wren && wreg_no == regno && (wreg_data & (1 << bitno)) & (wstrb[bitno/8] == 1);
    endfunction;

    function automatic logic [DATA_WIDTH-1:0] mask_write_bytes(input logic [DATA_WIDTH-1:0] r);
        integer	 i;
        logic [aximm.DATA_WIDTH-1:0] retval;;
        for ( i = 0; i < aximm.STRB_WIDTH; i = i+1 ) begin
            retval[(i*8) +: 8] = wstrb[i] ? wreg_data[(i*8) +: 8] : r[(i*8) +: 8];
        end
        return retval;
    endfunction   
endinterface

module piradip_axi4mmlite_subordinate (
        axi4mm_lite aximm,
        piradip_register_if reg_if
    );
    localparam integer DATA_WIDTH = $bits(aximm.wdata);
    localparam integer ADDR_WIDTH = $bits(aximm.awaddr);
    localparam integer ADDR_LSB = (DATA_WIDTH/32) + 1;
    localparam integer REGISTER_ADDR_BITS = ADDR_WIDTH - ADDR_LSB;
    
    import piradip_axi4::*;
      
    logic aw_en;
    logic [ADDR_WIDTH-1:0] awaddr_r;
    logic [ADDR_WIDTH-1:0] araddr_r;
    
    assign reg_if.rden = aximm.arready & aximm.arvalid & ~aximm.rvalid;

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;

    always @(posedge aximm.aclk) begin 
        if (~aximm.aresetn) begin
            aximm.awready <= 1'b0;
            aw_en <= 1'b1;
        end else if (~aximm.awready && aximm.awvalid && aximm.wvalid && aw_en) begin
            aximm.awready <= 1'b1;
            aw_en <= 1'b0;
        end else if (aximm.bready && aximm.bvalid) begin
            aw_en <= 1'b1;
            aximm.awready <= 1'b0;
        end else begin
            aximm.awready <= 1'b0;
        end
    end 
            
    always @(posedge aximm.aclk) begin
        if (~aximm.aresetn) begin
            aximm.wready <= 1'b0;
            awaddr_r <= 0;
        end else if (~aximm.wready && aximm.wvalid && aximm.awvalid && aw_en) begin
            aximm.wready <= 1'b1;
            awaddr_r <= aximm.awaddr;
            //reg_if.wreg_data <= aximm.wdata;
            //reg_if.wstrb <= aximm.wstrb;
        end else begin
            aximm.wready <= 1'b0;
        end
    end       
    
    always @(posedge aximm.aclk) begin
        if (~aximm.aresetn) begin
            aximm.arready <= 1'b0;
            araddr_r  <= 32'b0;
        end else if (~aximm.arready && aximm.arvalid) begin
            aximm.arready <= 1'b1;
            araddr_r  <= aximm.araddr;
        end else begin
            aximm.arready <= 1'b0;
        end
    end 
    
    assign reg_if.rreg_no = araddr_r[ADDR_LSB+REGISTER_ADDR_BITS-1:ADDR_LSB];
    assign reg_if.wreg_no = awaddr_r[ADDR_LSB+REGISTER_ADDR_BITS-1:ADDR_LSB];
	
	assign reg_if.wren = aximm.wready && aximm.wvalid && aximm.awready && aximm.awvalid;
	assign reg_if.wstrb = aximm.wstrb;
	assign reg_if.wreg_data = aximm.wdata;
	
    always @(posedge aximm.aclk) begin
        if (~aximm.aresetn) begin
            aximm.bvalid  <= 0;
            aximm.bresp   <= AXI_RESP_OKAY;
        end else if (aximm.awready && aximm.awvalid && ~aximm.bvalid && aximm.wready && aximm.wvalid) begin
            aximm.bvalid <= 1'b1;
            aximm.bresp  <= AXI_RESP_OKAY;
        end else if (aximm.bready && aximm.bvalid) begin
            aximm.bvalid <= 1'b0; 
        end
    end   	
    
    always @(posedge aximm.aclk) begin
        if (~aximm.aresetn) begin
            aximm.rvalid <= 0;
            aximm.rresp  <= AXI_RESP_OKAY;
        end else if (aximm.arready && aximm.arvalid && ~aximm.rvalid) begin
            aximm.rvalid <= 1'b1;
            aximm.rresp  <= AXI_RESP_OKAY; // 'OKAY' response
        end else if (aximm.rvalid && aximm.rready) begin
            aximm.rvalid <= 1'b0;
        end
    end    
	
    always @(posedge aximm.aclk) begin
        if (~aximm.aresetn) begin
            aximm.rdata  <= 0;
        end else if (reg_if.rden) begin
            aximm.rdata <= reg_if.rreg_data;
        end   
    end
endmodule

module register_to_stream #(
    parameter DATA_WIDTH = 32,
    parameter REGISTER_NO = 0
) (
    output logic do_issue,
    output logic failed_issue,
    output logic [DATA_WIDTH-1:0] read_data,
    piradip_register_if reg_if,
    axis_simple stream
);
    logic is_reg, busy;
    
    assign busy = (stream.tvalid & ~stream.tready);
    assign do_issue = is_reg & ~busy;
     
    assign read_data = { failed_issue, stream.tready };

    always_comb is_reg = reg_if.is_reg_write(REGISTER_NO);

    always @(posedge reg_if.aclk)
    begin
        stream.tlast <= 1'b0;
           
        if (~reg_if.aresetn | ~stream.aresetn) begin
            stream.tvalid <= 1'b0;
            failed_issue <= 1'b0;
        end else if (reg_if.is_reg_write(REGISTER_NO)) begin
            if (do_issue) begin
                stream.tvalid <= 1'b1;
            end else begin
                failed_issue <= 1;
            end
        end else begin
            failed_issue <= reg_if.is_reg_read(REGISTER_NO) ? 0 : failed_issue;
            stream.tvalid <= stream.tvalid & ~stream.tready;
        end
    end    
    
endmodule

