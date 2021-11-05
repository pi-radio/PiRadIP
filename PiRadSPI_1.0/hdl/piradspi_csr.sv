
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
`include "piradspi.svh"

import piradspi::*;

module piradspi_csr #(
    parameter NUM_PROFILES = 8
) (
    axi4mm_lite aximm,
    
    axis_simple axis_cmd,
    axis_simple axis_mosi,
    axis_simple axis_miso,
            
    output reg engine_enable,
    input wire engine_error,
    input wire engine_busy
);
	localparam integer DATA_WIDTH           = aximm.DATA_WIDTH;
    localparam integer ADDR_WIDTH	        = aximm.ADDR_WIDTH;
    localparam integer AXI_BYTE_WIDTH       = DATA_WIDTH/8;
    localparam integer ADDR_WORD_BITS       = $clog2(AXI_BYTE_WIDTH);
    localparam integer REGISTER_ADDR_BITS   = ADDR_WIDTH-ADDR_WORD_BITS;
    localparam SPI_IP_MAGIC                 = 32'h91700591;
	localparam SPI_IP_VER                   = 32'h00000100;
	localparam PROFILE_SELECT_WIDTH         = $clog2(NUM_PROFILES);

    typedef logic [DATA_WIDTH-1:0] axi_data_t;
	typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;
    typedef logic [PROFILE_SELECT_WIDTH-1:0] profile_id_t;

	
	localparam regno_t REGISTER_DEVID       = 'h00;
	localparam regno_t REGISTER_VER         = 'h01;
    localparam regno_t REGISTER_CTRLSTAT    = 'h02;

    localparam regno_t REGISTER_DEVSELECT   = 'h03;
    localparam regno_t REGISTER_PROFSELECT  = 'h04;
    localparam regno_t REGISTER_CMD_ID      = 'h05;
    
    localparam regno_t REGISTER_MOSIFIFO    = 'h06;
    localparam regno_t REGISTER_MISOFIFO    = 'h07;

    localparam regno_t REGISTER_TRIGGER     = 'h0F;

    localparam regno_t REGISTER_PROFBASE    = 'h10;
    localparam regno_t REGISTER_POLPHA      = 'h0;
    localparam regno_t REGISTER_SCLKDIV     = 'h1;
    localparam regno_t REGISTER_STARTWAIT   = 'h2;
    localparam regno_t REGISTER_CSNTOSCLK   = 'h3;
    localparam regno_t REGISTER_SCLKTOCSN   = 'h4;
    localparam regno_t REGISTER_XFERLEN     = 'h5;
    
    localparam regno_t REGISTER_PROFSIZE    = 'h8;   

    piradip_register_if #(
            .DATA_WIDTH(aximm.DATA_WIDTH), 
            .REGISTER_ADDR_BITS(sub_imp.REGISTER_ADDR_BITS)
        ) reg_if (
            .aclk(aximm.aclk), 
            .aresetn(aximm.aresetn)
        );

    piradip_axi4mmlite_subordinate sub_imp(.reg_if(reg_if.SERVER), .aximm(aximm), .*);



    logic do_cmd_issue, failed_cmd_issue;
    logic do_mosi_issue, failed_mosi_issue;
    
    register_to_stream #(.REGISTER_NO(REGISTER_TRIGGER)) cmd_reg_to_stream(
            .do_issue(do_cmd_issue),
            .failed_issue(failed_cmd_issue),
            .read_data(cmd_read_data),
            .stream(axis_cmd),
            .reg_if(reg_if)
        );

    register_to_stream #(.REGISTER_NO(REGISTER_MOSIFIFO)) mosi_reg_to_stream(
            .do_issue(do_cmd_issue),
            .failed_issue(failed_cmd_issue),
            .read_data(cmd_read_data),
            .stream(axis_miso),
            .reg_if(reg_if)
        );

    
    command_u_t cmd_out;
    
    assign axis_cmd.tdata = cmd_out.data;
        

    genvar i;

    reg autoinc_id;
    
    // TODO -- fix the width
    logic[15:0] cmd_id;
    logic[15:0] device_sel;
    typedef logic [7:0] wait_t;
    typedef logic [15:0] xfer_len_t;

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

    
	// Example-specific design signals
	// local parameter for addressing 32 bit / 64 bit DATA_WIDTH
	// ADDR_LSB is used for addressing 32/64 bit registers/memories
	// ADDR_LSB = 2 for 32 bits (n downto 2)
	// ADDR_LSB = 3 for 64 bits (n downto 3)

/*
	wire	 slv_reg_rden;
	wire	 slv_reg_wren;
    wire regno_t rreg_no;
    wire regno_t wreg_no;

	reg [DATA_WIDTH-1:0]	 rreg_data;
*/
    function logic is_profile_write(input integer i, 
            input logic [sub_imp.REGISTER_ADDR_BITS-1:0] rno);
        return reg_if.wren && (rno >= REGISTER_PROFBASE + i * REGISTER_PROFSIZE) &&
            (rno < (REGISTER_PROFBASE + (i + 1) * REGISTER_PROFSIZE));   
    endfunction
    
    localparam write_profile_reg_mask = (REGISTER_PROFSIZE - 1);
    
    logic [sub_imp.REGISTER_ADDR_BITS-1:0] write_profile_reg;
    
    assign write_profile_reg = (reg_if.wreg_no - REGISTER_PROFBASE);
    
    generate
        for (i = 0; i < NUM_PROFILES; i++) begin
            always @( posedge aximm.aclk )
            begin
                if (~aximm.aresetn) begin
                    profiles[i].cpol = 0;
                    profiles[i].cpha = 0;
                    profiles[i].sclk_cycles = 16'hFFFF;
                    profiles[i].wait_start = 16'hFFFF;
                    profiles[i].csn_to_sclk_cycles = 16'hFFFF;
                    profiles[i].sclk_to_csn_cycles = 16'hFFFF;        
                    profiles[i].xfer_len = 16'h8;
                end else if (is_profile_write(i, reg_if.wreg_no)) begin
                    case(write_profile_reg)
                    REGISTER_POLPHA: 
                        if (aximm.wstrb[0]) begin
                            { profiles[i].cpol, profiles[i].cpha } <= aximm.wdata;
                        end
                    REGISTER_SCLKDIV: profiles[i].sclk_cycles <= sub_imp.mask_write_bytes(profiles[i].sclk_cycles);
                    REGISTER_STARTWAIT: profiles[i].wait_start <=  sub_imp.mask_write_bytes(profiles[i].wait_start);
                    REGISTER_CSNTOSCLK: profiles[i].csn_to_sclk_cycles <= sub_imp.mask_write_bytes(profiles[i].csn_to_sclk_cycles);
                    REGISTER_SCLKTOCSN: profiles[i].sclk_to_csn_cycles <= sub_imp.mask_write_bytes(profiles[i].sclk_to_csn_cycles);
                    REGISTER_XFERLEN: profiles[i].xfer_len <= sub_imp.mask_write_bytes(profiles[i].xfer_len);
                    default: begin $display("Prof reg: %b", write_profile_reg); end                          
                    endcase
                end
            end
        end
    endgenerate

    assign error_clear = reg_if.is_reg_write(REGISTER_CTRLSTAT) & aximm.wdata[1];

    // Control Status
	always @(posedge aximm.aclk)
	begin
        if (~aximm.aresetn) begin
            autoinc_id <= 1'b0;
            engine_enable <= 1'b0;
        end else if (reg_if.is_reg_write(REGISTER_CTRLSTAT)) begin
            if (aximm.wstrb[0]) begin
                engine_enable <= aximm.wdata[0];
                autoinc_id <= aximm.wdata[3];
            end
        end
    end
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            cmd_id <= 0;
        end else if(reg_if.wren) begin
            case (reg_if.wreg_no)
            REGISTER_CMD_ID: begin
                cmd_id = sub_imp.mask_write_bytes(cmd_id);
            end
            REGISTER_TRIGGER: begin
                cmd_id <= cmd_id + 1;
            end
            endcase
        end
    end

    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            cmd_out.c.pad <= 0;
            cmd_out.c.cmd.cpol <= 0;
            cmd_out.c.cmd.cpha <= 0;
            cmd_out.c.cmd.id <= 0;
            cmd_out.c.cmd.device <= 0;
            cmd_out.c.cmd.sclk_cycles <= 0;
            cmd_out.c.cmd.wait_start <= 0;
            cmd_out.c.cmd.csn_to_sclk_cycles <= 0;
            cmd_out.c.cmd.sclk_to_csn_cycles <= 0;        
            cmd_out.c.cmd.xfer_len <= 0;
        end else if (do_cmd_issue) begin
            cmd_out.c.cmd.cpol <= profiles[profile_sel].cpol;
            cmd_out.c.cmd.cpha <= profiles[profile_sel].cpha;
            cmd_out.c.cmd.id <= cmd_id;
            cmd_out.c.cmd.device <= device_sel;
            cmd_out.c.cmd.sclk_cycles <= profiles[profile_sel].sclk_cycles;
            cmd_out.c.cmd.wait_start <= profiles[profile_sel].wait_start;
            cmd_out.c.cmd.csn_to_sclk_cycles <= profiles[profile_sel].csn_to_sclk_cycles;
            cmd_out.c.cmd.sclk_to_csn_cycles <= profiles[profile_sel].sclk_to_csn_cycles;
            cmd_out.c.cmd.xfer_len <= profiles[profile_sel].xfer_len;
        end
    end

    
	always @( posedge aximm.aclk )
    begin
        if (~aximm.aresetn) begin
            device_sel <= 0;
            profile_sel <= 0;
        end  else if (reg_if.wren) begin
            case (reg_if.wreg_no)
            REGISTER_DEVSELECT: begin
                device_sel = sub_imp.mask_write_bytes(device_sel);
            end
            REGISTER_PROFSELECT: begin
                profile_sel = sub_imp.mask_write_bytes(profile_sel);
            end
            default : begin
            end
            endcase
        end
    end  
    
    integer read_profile_no;
    integer read_profile_reg;
    profile_t read_profile;
    
    assign read_profile = profiles[read_profile_no];
    assign read_profile_no = (reg_if.rreg_no - REGISTER_PROFBASE) / REGISTER_PROFSIZE;
    assign read_profile_reg = (reg_if.rreg_no - REGISTER_PROFBASE) & (REGISTER_PROFSIZE - 1);
        
    always @(*) begin
        if (reg_if.rreg_no >= REGISTER_PROFBASE) begin
            case (read_profile_reg)
            REGISTER_POLPHA:
                reg_if.rreg_data <= { {{DATA_WIDTH-2}{1'b0}}, read_profile.cpol, read_profile.cpha };
            REGISTER_SCLKDIV: reg_if.rreg_data <= read_profile.sclk_cycles;
            REGISTER_STARTWAIT: reg_if.rreg_data <=  read_profile.wait_start;
            REGISTER_CSNTOSCLK: reg_if.rreg_data <= read_profile.csn_to_sclk_cycles;
            REGISTER_SCLKTOCSN: reg_if.rreg_data <= read_profile.sclk_to_csn_cycles;
            REGISTER_XFERLEN: reg_if.rreg_data <= read_profile.xfer_len;      
            endcase
        end else begin
            // Address decoding for reading registers
            case (reg_if.rreg_no)	      
            REGISTER_DEVID: reg_if.rreg_data <= SPI_IP_MAGIC;
            REGISTER_VER: reg_if.rreg_data <= SPI_IP_VER;
            // REGISTER_CTRLSTAT
            REGISTER_DEVSELECT: reg_if.rreg_data <= device_sel;
            REGISTER_PROFSELECT: reg_if.rreg_data <= profile_sel;
            REGISTER_CMD_ID: reg_if.rreg_data <= cmd_id; 
            REGISTER_MOSIFIFO: reg_if.rreg_data <= axis_mosi.tready ? 0 : {{DATA_WIDTH}{1'b1}};
            REGISTER_MISOFIFO: reg_if.rreg_data <= axis_miso.tdata;
            REGISTER_TRIGGER: reg_if.rreg_data <= { {{DATA_WIDTH-2}{1'b0}}, failed_cmd_issue, axis_cmd.tready};
            default: reg_if.rreg_data <= 0;
            endcase
        end
    end
endmodule
