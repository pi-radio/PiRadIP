
`timescale 1 ns / 1 ps

/*
    Register map
    
    Reg 00h: Control/Status
        Bit 0 - Enable(d)
        Bit 1 - Error
        Bit 2 - Busy
        Bit 3 - Autoincrement ID enable
        Bit 4 - 
    Reg 01h: 
    
    --- Command Programming
    Reg 10h: Device Select
    Reg 11h: Profile Select
    Reg 12h: Command ID
    Reg 18h: MOSI FIFO
    Reg 19h: MISO FIFO
    Reg 1Fh: Trigger
    
    -- Profiles start at 20h
    Reg 0h: POL/PHA
    Reg 1h: SCLK div
    Reg 2h: Start wait cycles
    Reg 3h: CSN assert to SCLK cycles
    Reg 4h: SCLK to CSN deassert cycles
    Reg 5h: Transfer Length    
*/

	module piradspi_csr #
	(
        type spi_types = piradspi_types.inst,
		parameter integer C_S_AXI_DATA_WIDTH	= 32,
		parameter integer C_S_AXI_ADDR_WIDTH	= 8,
		parameter integer NUM_PROFILES          = 8
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
		input wire  s_axi_rready,
		
		axis_simple axis_cmd,
		axis_simple axis_mosi,
		axis_simple axis_miso,
		piradspi_support support,
		        
        output reg engine_enable,
        input wire engine_error,
        input wire engine_busy
	);
	
	localparam SPI_IP_MAGIC         = 32'h91700591;
	localparam SPI_IP_VER           = 32'h00000100;
	localparam PROFILE_SELECT_WIDTH = $clog2(NUM_PROFILES);
	
	localparam REGISTER_DEVID       = 'h00;
	localparam REGISTER_VER         = 'h01;
    localparam REGISTER_CTRLSTAT    = 'h02;

    localparam REGISTER_DEVSELECT   = 'h10;
    localparam REGISTER_PROFSELECT  = 'h11;
    localparam REGISTER_CMD_ID      = 'h12;
    
    localparam REGISTER_MOSIFIFO    = 'h18;
    localparam REGISTER_MISOFIFO    = 'h19;

    localparam REGISTER_TRIGGER     = 'h1F;

    localparam REGISTER_PROFBASE    = 'h20;
    localparam REGISTER_POLPHA      = 'h0;
    localparam REGISTER_SCLKDIV     = 'h1;
    localparam REGISTER_STARTWAIT   = 'h2;
    localparam REGISTER_CSNTOSCLK   = 'h3;
    localparam REGISTER_SCLKTOCSN   = 'h4;
    localparam REGISTER_XFERLEN     = 'h5;
    
    localparam REGISTER_PROFSIZE    = 'h10;   

    typedef logic [PROFILE_SELECT_WIDTH-1:0] profile_id_t;

    genvar i;

    reg autoinc_id;
    
    spi_types::cmd_id_t cmd_id;
    spi_types::dev_id_t device_sel;
    profile_id_t profile_sel;
    
    typedef struct packed {
        logic       cpol;
        logic       cpha;
        wait_t      sclk_cycles;
        wait_t      wait_start;
        wait_t      csn_to_sclk_cycles;
        wait_t      sclk_to_csn_cycles;        
        xfer_len_t  xfer_len;
    } profile_t;

    profile_t profiles[0:NUM_PROFILES-1];

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

	// Example-specific design signals
	// local parameter for addressing 32 bit / 64 bit C_S_AXI_DATA_WIDTH
	// ADDR_LSB is used for addressing 32/64 bit registers/memories
	// ADDR_LSB = 2 for 32 bits (n downto 2)
	// ADDR_LSB = 3 for 64 bits (n downto 3)
	localparam integer ADDR_LSB = (C_S_AXI_DATA_WIDTH/32) + 1;
    localparam integer REGISTER_ADDR_BITS = C_S_AXI_ADDR_WIDTH - ADDR_LSB;

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;

	wire	 slv_reg_rden;
	wire	 slv_reg_wren;
    wire regno_t rreg_addr;
    wire regno_t wreg_addr;

	reg [C_S_AXI_DATA_WIDTH-1:0]	 reg_data_out;
	
	reg	 aw_en;

	// I/O Connections assignments

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
	
    always @(posedge s_axi_aclk) begin 
        if (~s_axi_aresetn) begin
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

    always @(posedge s_axi_aclk) begin
        if (~s_axi_aresetn) begin
            axi_awaddr <= 0;
        end else if (~axi_awready && s_axi_awvalid && s_axi_wvalid && aw_en) begin
            axi_awaddr <= s_axi_awaddr;
        end 
    end       

    always @(posedge s_axi_aclk) begin
        if ( ~s_axi_aresetn ) begin
            axi_wready <= 1'b0;
        end else if (~axi_wready && s_axi_wvalid && s_axi_awvalid && aw_en ) begin
            axi_wready <= 1'b1;
        end else begin
            axi_wready <= 1'b0;
        end
    end       

	assign slv_reg_wren = axi_wready && s_axi_wvalid && axi_awready && s_axi_awvalid;

    integer write_profile_no;
    integer write_profile_reg;
    profile_t write_profile;
    
    function automatic logic [C_S_AXI_DATA_WIDTH-1:0] axi_write_bytes(input logic [C_S_AXI_DATA_WIDTH-1:0] r);
        integer	 byte_index;
        for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 ) begin
            if ( s_axi_wstrb[byte_index] == 1 ) begin
            // Respective byte enables are asserted as per write strobes 
            // Slave register 1
                r[(byte_index*8) +: 8] <= s_axi_wdata[(byte_index*8) +: 8];
            end
        end
        return r;     
    endfunction

    generate
        for (i = 0; i < NUM_PROFILES; i++) begin
            always @( posedge s_axi_aclk )
            begin
                if (~s_axi_aresetn) begin
                    profiles[i].cpol = 0;
                    profiles[i].cpha = 0;
                    profiles[i].sclk_cycles = 16'hFFFF;
                    profiles[i].wait_start = 16'hFFFF;
                    profiles[i].csn_to_sclk_cycles = 16'hFFFF;
                    profiles[i].sclk_to_csn_cycles = 16'hFFFF;        
                    profiles[i].xfer_len = 16'h8;
                end else if (slv_reg_wren && 
                        wreg_addr >= REGISTER_PROFBASE + i * REGISTER_PROFSIZE &&
                        wreg_addr < REGISTER_PROFBASE + (i + 1) * REGISTER_PROFSIZE) begin
                    case(write_profile_reg)
                    REGISTER_POLPHA: 
                        if (s_axi_wstrb[0]) begin
                            { profiles[i].cpol, profiles[i].cpha } <= s_axi_wdata;
                        end
                    REGISTER_SCLKDIV: profiles[i].sclk_cycles <= axi_write_bytes(profiles[i].sclk_cycles);
                    REGISTER_STARTWAIT: profiles[i].wait_start <=  axi_write_bytes(profiles[i].wait_start);
                    REGISTER_CSNTOSCLK: profiles[i].csn_to_sclk_cycles <= axi_write_bytes(profiles[i].csn_to_sclk_cycles);
                    REGISTER_SCLKTOCSN: profiles[i].sclk_to_csn_cycles <= axi_write_bytes(profiles[i].sclk_to_csn_cycles);
                    REGISTER_XFERLEN: profiles[i].xfer_len <= axi_write_bytes(profiles[i].xfer_len);                          
                    endcase
                end
            end
        end
    endgenerate


    assign error_clear = (wreg_addr == REGISTER_CTRLSTAT) & slv_reg_wren & s_axi_wdata[1];

    // Control Status
	always @(posedge s_axi_aclk)
	begin
        if (~s_axi_aresetn) begin
            autoinc_id <= 1'b0;
            engine_enable <= 1'b0;
        end else if (wreg_addr == REGISTER_CTRLSTAT && slv_reg_wren) begin
            if (s_axi_wstrb[0]) begin
                engine_enable <= s_axi_wdata[0];
                autoinc_id <= s_axi_wdata[3];
            end
        end
    end

    
    always @(posedge s_axi_aclk)
    begin
        if (~s_axi_aresetn) begin
            cmd_id <= 0;
        end else if(slv_reg_wren) begin
            case (wreg_addr)
            REGISTER_CMD_ID: begin
                cmd_id = axi_write_bytes(cmd_id);
            end
            REGISTER_TRIGGER: begin
                cmd_id <= cmd_id + 1;
            end
            endcase
        end
    end
    
	always @( posedge s_axi_aclk )
	begin
	  if ( ~s_axi_aresetn )
	    begin
           device_sel <= 0;
	    end 
	  else if (slv_reg_wren) begin
	        case (wreg_addr)
	           REGISTER_DEVSELECT: begin
	               device_sel = axi_write_bytes(device_sel);
	           end
	           REGISTER_PROFSELECT: begin
	               device_sel = axi_write_bytes(profile_sel);
	           end


/*
	          2'h1:
	            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
	              if ( s_axi_wstrb[byte_index] == 1 ) begin
	                // Respective byte enables are asserted as per write strobes 
	                // Slave register 1
	                slv_reg1[(byte_index*8) +: 8] <= s_axi_wdata[(byte_index*8) +: 8];
	              end  
	          2'h2:
	            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
	              if ( s_axi_wstrb[byte_index] == 1 ) begin
	                // Respective byte enables are asserted as per write strobes 
	                // Slave register 2
	                slv_reg2[(byte_index*8) +: 8] <= s_axi_wdata[(byte_index*8) +: 8];
	              end  
	          2'h3:
	            for ( byte_index = 0; byte_index <= (C_S_AXI_DATA_WIDTH/8)-1; byte_index = byte_index+1 )
	              if ( s_axi_wstrb[byte_index] == 1 ) begin
	                // Respective byte enables are asserted as per write strobes 
	                // Slave register 3
	                slv_reg3[(byte_index*8) +: 8] <= s_axi_wdata[(byte_index*8) +: 8];
	              end  
*/	                    
	          default : begin
/*
	                      slv_reg0 <= slv_reg0;
	                      slv_reg1 <= slv_reg1;
	                      slv_reg2 <= slv_reg2;
	                      slv_reg3 <= slv_reg3;
                      */
                    end
	        endcase
	      end
	  end  

    always @(posedge s_axi_aclk) begin
        if (~s_axi_aresetn) begin
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
    
    integer read_profile_no;
    integer read_profile_reg;
    profile_t read_profile;
    
    assign read_profile = profiles[read_profile_no];
    assign read_profile_no = (rreg_addr - REGISTER_PROFBASE) / REGISTER_PROFSIZE;
    assign read_profile_reg = (rreg_addr - REGISTER_PROFBASE) & (REGISTER_PROFSIZE - 1);
    
    // Implement memory mapped register select and read logic generation
    // Slave register read enable is asserted when valid address is available
    // and the slave is ready to accept the read address.
    assign slv_reg_rden = axi_arready & s_axi_arvalid & ~axi_rvalid;
    always @(*) begin
        if (rreg_addr >= REGISTER_PROFBASE) begin
            case (read_profile_reg)
            REGISTER_POLPHA:
                reg_data_out <= { {{C_S_AXI_DATA_WIDTH-2}{1'b0}}, read_profile.cpol, read_profile.cpha };
            REGISTER_SCLKDIV: reg_data_out <= read_profile.sclk_cycles;
            REGISTER_STARTWAIT: reg_data_out <=  read_profile.wait_start;
            REGISTER_CSNTOSCLK: reg_data_out <= read_profile.csn_to_sclk_cycles;
            REGISTER_SCLKTOCSN: reg_data_out <= read_profile.sclk_to_csn_cycles;
            REGISTER_XFERLEN: reg_data_out <= read_profile.xfer_len;      
            endcase
        end else begin
            // Address decoding for reading registers
            case (rreg_addr)	      
            REGISTER_DEVID: reg_data_out <= SPI_IP_MAGIC;
            REGISTER_VER: reg_data_out <= SPI_IP_MAGIC;
            // REGISTER_CTRLSTAT
            REGISTER_DEVSELECT: reg_data_out <= device_sel;
            REGISTER_PROFSELECT: reg_data_out <= profile_sel;
            REGISTER_CMD_ID: reg_data_out <= cmd_id; 
            REGISTER_MOSIFIFO: reg_data_out <= mosi_ready ? 0 : {{C_S_AXI_DATA_WIDTH}{1'b1}};
            REGISTER_MISOFIFO: reg_data_out <= miso_data;
            REGISTER_TRIGGER: reg_data_out <= cmd_ready ? 0 : {{C_S_AXI_DATA_WIDTH}{1'b1}};
            default : reg_data_out <= 0;
            endcase
        end
    end
    
    always @(posedge s_axi_aclk) begin
        if (~s_axi_aresetn) begin
            axi_rdata  <= 0;
        end else if (slv_reg_rden) begin
            axi_rdata <= reg_data_out;
        end   
    end   

endmodule
