`timescale 1 ns / 1 ps

/*
    Register map
    
    Reg 00h: Control/Status
        Bit 0 - Enable(d)
        Bit 1 - Error
        Bit 2 - Busy
        Bit 3 - Autoincrement ID enable
        Bit 4 - Interrupt Asserted
        Bit 5 - Interrupt Enable
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
module piradspi_csr #(
    parameter NUM_PROFILES = 8,
    parameter DATA_WIDTH = 32,
    parameter ADDR_WIDTH = 10,
    parameter DEBUG=1
) (
    axi4mm_lite.SUBORDINATE aximm,
    
    axis_simple.MANAGER axis_cmd,
    axis_simple.MANAGER axis_mosi,
    axis_simple.SUBORDINATE axis_miso,
            
    output logic engine_enable,
    input logic engine_error,
    input logic engine_busy,
    input logic command_completed,
    output logic intr_out
);
    import piradspi::*;

    localparam integer AXI_BYTE_WIDTH       = DATA_WIDTH/8;
    localparam integer ADDR_WORD_BITS       = $clog2(AXI_BYTE_WIDTH);
    localparam integer REGISTER_ADDR_BITS   = ADDR_WIDTH - ADDR_WORD_BITS; //aximm.ADDR_WIDTH-ADDR_WORD_BITS;
	localparam PROFILE_SELECT_WIDTH         = $clog2(NUM_PROFILES);

    //localparam integer REGISTER_ADDR_LSB = AXI4MM_REGISTER_ADDR_LSB(DATA_WIDTH, ADDR_WIDTH);

    typedef logic [DATA_WIDTH-1:0] axi_data_t;
	typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;
    typedef logic [PROFILE_SELECT_WIDTH-1:0] profile_id_t;

    localparam WRITE_PROFILE_REG_MASK = (REGISTER_PROFSIZE - 1);
    
    piradip_register_if reg_if (
            .aclk(aximm.aclk), 
            .aresetn(aximm.aresetn)
        );

    piradip_axi4mmlite_subordinate sub_imp(.reg_if(reg_if.SERVER), .aximm(aximm), .*);

    axi_data_t ctrlstat_out;
    
    genvar i;

    logic autoinc_id;
    
    // TODO -- fix the width
    logic[15:0] cmd_id;
    logic[15:0] device_sel;
    typedef logic [7:0] wait_t;
    typedef logic [15:0] xfer_len_t;
    logic intr_en, intr_assert;

    axi_data_t completion_count;

    profile_id_t profile_sel;

    always_comb ctrlstat_out = {  axis_miso.tvalid, axis_mosi.tready, intr_en, intr_assert, autoinc_id, engine_busy, engine_error, engine_enable };

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
            .do_issue(do_mosi_issue),
            .failed_issue(failed_mosi_issue),
            .read_data(mosi_read_data),
            .stream(axis_mosi),
            .reg_if(reg_if)
        );

    
    command_u_t cmd_out;
    
    assign axis_cmd.tdata = cmd_out.data;
        

    
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

    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            completion_count = 0;
        end else begin
            completion_count = (reg_if.is_reg_write(REGISTER_CMPLCNT) ? 0 : completion_count) +
                (command_completed ? 1 : 0);
        end
    end
    
    always_comb intr_out = intr_assert & intr_en;
 
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            intr_en <= 0;
        end else begin
            intr_en <= reg_if.reg_update_bit(REGISTER_CTRLSTAT, CTRLSTAT_INTREN, intr_en);
        end
    end
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            intr_assert <= 0;
        end else begin
            intr_assert <= (reg_if.is_reg_bit_set(REGISTER_CTRLSTAT, CTRLSTAT_INTR) | 
                    reg_if.is_reg_write(REGISTER_INTRACK)) ? 0 :
                (command_completed ? 1 : intr_assert);
        end
    end
    
    function automatic logic [DATA_WIDTH-1:0] mask_write_bytes(input logic [DATA_WIDTH-1:0] r);
        integer	 i;
        logic [aximm.DATA_WIDTH-1:0] retval;;
        for ( i = 0; i < aximm.STRB_WIDTH; i = i+1 ) begin
            retval[(i*8) +: 8] = aximm.wstrb[i] ? aximm.wdata[(i*8) +: 8] : r[(i*8) +: 8];
        end
        return retval;
        //WHYYYYYYYY won't this reference work in synthesis
        //return sub_imp.mask_write_bytes(r);     
    endfunction

    generate
        for (i = 0; i < NUM_PROFILES; i++) begin
            logic [REGISTER_ADDR_BITS-1:0] write_profile_reg;

            function logic is_profile_write(input regno_t rno);
                return reg_if.wren && (rno >= REGISTER_PROFBASE + i * REGISTER_PROFSIZE) &&
                    (rno < (REGISTER_PROFBASE + (i + 1) * REGISTER_PROFSIZE));   
            endfunction
        
            assign write_profile_reg = (reg_if.wreg_no - REGISTER_PROFBASE) & WRITE_PROFILE_REG_MASK;
            
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
                end else if (is_profile_write(reg_if.wreg_no)) begin
                    case(write_profile_reg)
                    REGISTER_POLPHA: 
                        if (aximm.wstrb[0]) begin
                            { profiles[i].cpol, profiles[i].cpha } <= aximm.wdata;
                        end
                    REGISTER_SCLKDIV: profiles[i].sclk_cycles <= reg_if.mask_write_bytes(profiles[i].sclk_cycles);
                    REGISTER_STARTWAIT: profiles[i].wait_start <=  reg_if.mask_write_bytes(profiles[i].wait_start);
                    REGISTER_CSNTOSCLK: profiles[i].csn_to_sclk_cycles <= reg_if.mask_write_bytes(profiles[i].csn_to_sclk_cycles);
                    REGISTER_SCLKTOCSN: profiles[i].sclk_to_csn_cycles <= reg_if.mask_write_bytes(profiles[i].sclk_to_csn_cycles);
                    REGISTER_XFERLEN: profiles[i].xfer_len <= reg_if.mask_write_bytes(profiles[i].xfer_len);
                    default: begin $display("Prof reg: %b", write_profile_reg); end                          
                    endcase
                end
            end
        end
    endgenerate

    assign error_clear = reg_if.is_reg_write(REGISTER_CTRLSTAT) & aximm.wdata[1] & aximm.wstrb[0];

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
                cmd_id = mask_write_bytes(cmd_id);
            end
            REGISTER_TRIGGER: begin
                if (autoinc_id) cmd_id <= cmd_id + 1;
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
            axis_mosi.tdata <= 0;
        end  else if (reg_if.wren) begin
            case (reg_if.wreg_no)
            REGISTER_DEVSELECT: begin
                device_sel = mask_write_bytes(device_sel);
            end
            REGISTER_PROFSELECT: begin
                profile_sel = mask_write_bytes(profile_sel);
            end
            REGISTER_MOSIFIFO: begin
                axis_mosi.tdata = mask_write_bytes(axis_mosi.tdata);
            end
            default : begin
            end
            endcase
        end
    end  
    
    integer read_profile_no;
    integer read_profile_reg;
    profile_t read_profile;
    logic read_miso;
    
    assign read_profile = profiles[read_profile_no];
    assign read_profile_no = (reg_if.rreg_no - REGISTER_PROFBASE) / REGISTER_PROFSIZE;
    assign read_profile_reg = (reg_if.rreg_no - REGISTER_PROFBASE) & (REGISTER_PROFSIZE - 1);
    assign read_miso =  reg_if.rden && reg_if.rreg_no == REGISTER_MISOFIFO;
    assign axis_miso.tready = (~axis_miso.aresetn) ? 1'b0 : read_miso;
    
    always @(*) 
    begin
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
            REGISTER_CTRLSTAT: reg_if.rreg_data <= ctrlstat_out;
            REGISTER_DEVSELECT: reg_if.rreg_data <= device_sel;
            REGISTER_PROFSELECT: reg_if.rreg_data <= profile_sel;
            REGISTER_CMD_ID: reg_if.rreg_data <= cmd_id; 
            REGISTER_TRIGGER: reg_if.rreg_data <= cmd_read_data;
            REGISTER_MOSIFIFO: reg_if.rreg_data <= mosi_read_data;
            REGISTER_MISOFIFO: reg_if.rreg_data <= axis_miso.tvalid ? axis_miso.tdata : {{DATA_WIDTH}{1'b1}};
            REGISTER_TRIGGER: reg_if.rreg_data <= { {{DATA_WIDTH-2}{1'b0}}, failed_cmd_issue, axis_cmd.tready};
            default: reg_if.rreg_data <= 0;
            endcase
        end
    end
endmodule
