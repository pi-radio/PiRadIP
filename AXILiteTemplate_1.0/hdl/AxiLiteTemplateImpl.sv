`timescale 1 ns / 1 ps

module AXILiteTemplate #
(
    parameter integer C_S_AXI_DATA_WIDTH	= 32,
    parameter integer C_S_AXI_ADDR_WIDTH	= 4
)
(
    input wire  s_axi_aclk,
    input wire  s_axi_aresetn,
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] s_axi_awaddr,
    input wire [2 : 0] s_axi_awprot,
    input wire  s_axi_awvalid,
    output wire  s_axi_awready,
    input wire [C_S_AXI_DATA_WIDTH-1 : 0] s_axi_wdata,
    input wire [(C_S_AXI_DATA_WIDTH/8)-1 : 0] s_axi_wstrb,
    input wire  s_axi_wvalid,
    output wire  s_axi_wready,
    output wire [1 : 0] s_axi_bresp,
    output wire  s_axi_bvalid,
    input wire  s_axi_bready,
    input wire [C_S_AXI_ADDR_WIDTH-1 : 0] s_axi_araddr,
    input wire [2 : 0] s_axi_arprot,
    input wire  s_axi_arvalid,
    output wire  s_axi_arready,
    output wire [C_S_AXI_DATA_WIDTH-1 : 0] s_axi_rdata,
    output wire [1 : 0] s_axi_rresp,
    output wire  s_axi_rvalid,
    input wire  s_axi_rready
);
    localparam integer ADDR_LSB = (C_S_AXI_DATA_WIDTH/32) + 1;
    localparam integer REGISTER_ADDR_BITS = C_S_AXI_ADDR_WIDTH - ADDR_LSB;

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;
    typedef logic [C_S_AXI_DATA_WIDTH-1:0] axiword_t;
    
    // AXI4LITE signals
    reg [C_S_AXI_ADDR_WIDTH-1 : 0] 	axi_awaddr;
    reg  	axi_awready;
    reg  	axi_wready;
    reg [1 : 0] 	axi_bresp;
    reg  	axi_bvalid;
    reg [C_S_AXI_ADDR_WIDTH-1 : 0] 	axi_araddr;
    reg  	axi_arready;
    reg [C_S_AXI_DATA_WIDTH-1 : 0] 	axi_rdata;
    reg [1 : 0] 	axi_rresp;
    reg  	axi_rvalid;

    reg [C_S_AXI_DATA_WIDTH-1:0]	slv_reg0;
    reg [C_S_AXI_DATA_WIDTH-1:0]	slv_reg1;
    reg [C_S_AXI_DATA_WIDTH-1:0]	slv_reg2;
    reg [C_S_AXI_DATA_WIDTH-1:0]	slv_reg3;

    wire	 slv_reg_rden;
    wire	 slv_reg_wren;
    reg [C_S_AXI_DATA_WIDTH-1:0]	 reg_data_out;
    integer	 byte_index;
    reg	 aw_en;
    
    assign s_axi_awready	= axi_awready;
    assign s_axi_wready	= axi_wready;
    assign s_axi_bresp	= axi_bresp;
    assign s_axi_bvalid	= axi_bvalid;
    assign s_axi_arready	= axi_arready;
    assign s_axi_rdata	= axi_rdata;
    assign s_axi_rresp	= axi_rresp;
    assign s_axi_rvalid	= axi_rvalid;

	assign rreg_addr = axi_araddr[ADDR_LSB+REGISTER_ADDR_BITS:ADDR_LSB];
    assign wreg_addr = axi_awaddr[ADDR_LSB+REGISTER_ADDR_BITS:ADDR_LSB];

    assign slv_reg_wren = axi_wready && s_axi_wvalid && axi_awready && s_axi_awvalid;

    function automatic axi_write_bytes(ref logic [C_S_AXI_DATA_WIDTH-1:0] r);
        integer	 byte_index;
        for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 ) begin
            if ( s_axi_wstrb[byte_index] == 1 ) begin
            // Respective byte enables are asserted as per write strobes 
            // Slave register 1
                r[(byte_index*8) +: 8] <= s_axi_wdata[(byte_index*8) +: 8];
            end
        end     
    endfunction
    
    always @(posedge s_axi_aclk) begin 
        if (s_axi_aresetn == 1'b0) begin
            axi_awready <= 1'b0;
            aw_en <= 1'b1;
        end else if (~axi_awready && s_axi_awvalid && s_axi_wvalid && aw_en) begin
            axi_awready <= 1'b1;
            aw_en <= 1'b0;
        end else if (s_axi_bready && axi_bvalid) begin
            aw_en <= 1'b1;
            axi_awready <= 1'b0;
        end else begin
            axi_awready <= 1'b0;
        end
    end 
    
    // Implement axi_awaddr latching
    // This process is used to latch the address when both 
    // s_axi_awvalid and s_axi_wvalid are valid. 
    always @(posedge s_axi_aclk) begin
        if ( s_axi_aresetn == 1'b0 ) begin
            axi_awaddr <= 0;
        end else if (~axi_awready && s_axi_awvalid && s_axi_wvalid && aw_en) begin
            axi_awaddr <= s_axi_awaddr;
        end 
    end       
    
    // Implement axi_wready generation
    // axi_wready is asserted for one s_axi_aclk clock cycle when both
    // s_axi_awvalid and s_axi_wvalid are asserted. axi_wready is 
    // de-asserted when reset is low. 
     always @(posedge s_axi_aclk) begin
        if ( s_axi_aresetn == 1'b0 ) begin
            axi_wready <= 1'b0;
        end else if (~axi_wready && s_axi_wvalid && s_axi_awvalid && aw_en ) begin
            axi_wready <= 1'b1;
        end else begin
            axi_wready <= 1'b0;
        end
    end       
    
    
    always @(posedge s_axi_aclk)
 begin
        if (s_axi_aresetn == 1'b0) begin
            slv_reg0 <= 0;
            slv_reg1 <= 0;
            slv_reg2 <= 0;
            slv_reg3 <= 0;
        end else begin
            if (slv_reg_wren) begin
                case ( wreg_addr )
                    2'h0: axi_write_bytes(slv_reg0);
                    2'h1: axi_write_bytes(slv_reg1);
                    2'h2: axi_write_bytes(slv_reg2);
                    2'h3: axi_write_bytes(slv_reg3);
                    default : begin
                        slv_reg0 <= slv_reg0;
                        slv_reg1 <= slv_reg1;
                        slv_reg2 <= slv_reg2;
                        slv_reg3 <= slv_reg3;
                    end
                endcase
            end
        end
    end    
    
    always @(posedge s_axi_aclk) begin
        if (s_axi_aresetn == 1'b0) begin
            axi_bvalid  <= 0;
            axi_bresp   <= 2'b0;
        end else if (axi_awready && s_axi_awvalid && ~axi_bvalid && axi_wready && s_axi_wvalid) begin
            axi_bvalid <= 1'b1;
            axi_bresp  <= 2'b0; // 'OKAY' response 
        end else if (s_axi_bready && axi_bvalid) begin
            axi_bvalid <= 1'b0; 
        end
    end 

    always @(posedge s_axi_aclk) begin
        if (~s_axi_aresetn) begin
            axi_arready <= 1'b0;
            axi_araddr  <= 32'b0;
        end else if (~axi_arready && s_axi_arvalid) begin
            axi_arready <= 1'b1;
            axi_araddr  <= s_axi_araddr;
        end else begin
            axi_arready <= 1'b0;
        end
    end        

    always @(posedge s_axi_aclk) begin
        if (~s_axi_aresetn) begin
            axi_rvalid <= 0;
            axi_rresp  <= 0;
        end else if (axi_arready && s_axi_arvalid && ~axi_rvalid) begin
            axi_rvalid <= 1'b1;
            axi_rresp  <= 2'b0; // 'OKAY' response
        end else if (axi_rvalid && s_axi_rready) begin
            axi_rvalid <= 1'b0;
        end
    end    
    

    
    // Implement memory mapped register select and read logic generation
    // Slave register read enable is asserted when valid address is available
    // and the slave is ready to accept the read address.
    assign slv_reg_rden = axi_arready & s_axi_arvalid & ~axi_rvalid;
    always @(*)
    begin
          // Address decoding for reading registers
          case (rreg_addr)
            2'h0   : reg_data_out <= slv_reg0;
            2'h1   : reg_data_out <= slv_reg1;
            2'h2   : reg_data_out <= slv_reg2;
            2'h3   : reg_data_out <= slv_reg3;
            default : reg_data_out <= 0;
          endcase
    end
    
    always @( posedge s_axi_aclk )
 begin
        if (~s_axi_aresetn) begin
            axi_rdata  <= 0;
        end else if (slv_reg_rden) begin
            axi_rdata <= reg_data_out;
        end   
    end    
endmodule
