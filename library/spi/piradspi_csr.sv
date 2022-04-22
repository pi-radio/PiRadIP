`timescale 1ns/1ps

module piradspi_csr #(
                      parameter integer NUM_PROFILES = 8
                      ) 
   (    
        output logic engine_enable,
        input logic  engine_error,
        input logic  engine_busy,
        input logic  command_completed,
        output logic intr_out,
        piradspi_cmd_stream.MANAGER cmd_stream,
        axis_simple.MANAGER axis_mosi,
        axis_simple.SUBORDINATE axis_miso,
        axi4mm_lite.SUBORDINATE csr        
    );
   
   import piradspi_pkg::*;

   typedef csr.data_t csr_data_t;
   
   
   generate
      localparam integer CSR_DATA_WIDTH = $bits(csr.wdata);
      localparam integer CSR_ADDR_WIDTH = $bits(csr.awaddr);
      localparam integer STRB_WIDTH = CSR_DATA_WIDTH/8;
      localparam integer REGISTER_ADDR_BITS = CSR_ADDR_WIDTH - $clog2(STRB_WIDTH);
      localparam integer PROFILE_SELECT_WIDTH = $clog2(NUM_PROFILES);

      piradip_register_if #(
                            .DATA_WIDTH(CSR_DATA_WIDTH), 
                            .REGISTER_ADDR_BITS(REGISTER_ADDR_BITS)
                            ) reg_if (
                                      .aclk(csr.aclk), 
                                      .aresetn(csr.aresetn)
                                      );
   endgenerate

   csr_data_t ctrlstat_out;
   csr_data_t completion_count;
   csr_data_t mosi_read_data;
     
   typedef logic [PROFILE_SELECT_WIDTH-1:0] profile_id_t;

   localparam WRITE_PROFILE_REG_MASK = (REGISTER_PROFSIZE - 1);
   

   piradip_axi4mmlite_subordinate sub_imp(.reg_if(reg_if.SERVER), .aximm(csr));

   
   genvar                                   i;

   logic                                    autoinc_id;
   
   // TODO -- fix the width
   logic [15:0]                             cmd_id;
   logic [15:0]                             device_sel;
   typedef logic [7:0]                      wait_t;
   typedef logic [15:0]                     xfer_len_t;
   logic                                    intr_en, intr_assert;


   profile_id_t profile_sel;

   always_comb ctrlstat_out = {  axis_miso.tvalid, axis_mosi.tready, intr_en, intr_assert, autoinc_id, engine_busy, engine_error, engine_enable };

   logic                                    cmd_do_issue, cmd_failed_issue;
   logic                                    do_mosi_issue, failed_mosi_issue;
   
   register_to_stream 
     #(.REGISTER_NO(REGISTER_MOSIFIFO)) 
   mosi_reg_to_stream
     (
      .do_issue(do_mosi_issue),
      .failed_issue(failed_mosi_issue),
      .read_data(mosi_read_data),
      .stream(axis_mosi),
      .reg_if(reg_if.CLIENT)
      );
   
   typedef struct                           packed {
      logic                                 cpol;
      logic                                 cpha;
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

   always @(posedge csr.aclk)
     begin
        if (~csr.aresetn) begin
           completion_count = 0;
        end else begin
           completion_count = (reg_if.is_reg_write(REGISTER_CMPLCNT) ? 0 : completion_count) +
                              (command_completed ? 1 : 0);
        end
     end
   
   always_comb intr_out = intr_assert & intr_en;
   
   always @(posedge csr.aclk)
     begin
        if (~csr.aresetn) begin
           intr_en <= 0;
        end else begin
           intr_en <= reg_if.reg_update_bit(REGISTER_CTRLSTAT, CTRLSTAT_INTREN, intr_en);
        end
     end
   
   always @(posedge csr.aclk)
     begin
        if (~csr.aresetn) begin
           intr_assert <= 0;
        end else begin
           intr_assert <= (reg_if.is_reg_bit_set(REGISTER_CTRLSTAT, CTRLSTAT_INTR) | 
                           reg_if.is_reg_write(REGISTER_INTRACK)) ? 0 :
                          (command_completed ? 1 : intr_assert);
        end
     end
   
   function automatic logic [CSR_DATA_WIDTH-1:0] mask_write_bytes(input logic [CSR_DATA_WIDTH-1:0] r);
      integer	 i;
      logic [CSR_DATA_WIDTH-1:0] retval;
      for ( i = 0; i < STRB_WIDTH; i = i+1 ) begin
         retval[(i*8) +: 8] = csr.wstrb[i] ? csr.wdata[(i*8) +: 8] : r[(i*8) +: 8];
      end
      return retval;
      //WHYYYYYYYY won't this reference work in synthesis
      //return sub_imp.mask_write_bytes(r);     
   endfunction

   generate
      for (i = 0; i < NUM_PROFILES; i++) begin
         logic [REGISTER_ADDR_BITS-1:0] write_profile_reg;
         logic                          is_profile_write;


         assign is_profile_write = reg_if.wren && 
                                   (reg_if.wreg_no >= REGISTER_PROFBASE + i * REGISTER_PROFSIZE) &&
                                   (reg_if.wreg_no < (REGISTER_PROFBASE + (i + 1) * REGISTER_PROFSIZE));   
         
         assign write_profile_reg = (reg_if.wreg_no - REGISTER_PROFBASE) & WRITE_PROFILE_REG_MASK;
         
         always @( posedge csr.aclk )
           begin
              if (~csr.aresetn) begin
                 profiles[i].cpol = 0;
                 profiles[i].cpha = 0;
                 profiles[i].sclk_cycles = 16'hFFFF;
                 profiles[i].wait_start = 16'hFFFF;
                 profiles[i].csn_to_sclk_cycles = 16'hFFFF;
                 profiles[i].sclk_to_csn_cycles = 16'hFFFF;        
                 profiles[i].xfer_len = 16'h8;
              end else if (is_profile_write) begin
                 case(write_profile_reg)
                   REGISTER_POLPHA: 
                     if (csr.wstrb[0]) begin
                        { profiles[i].cpol, profiles[i].cpha } <= csr.wdata;
                     end
                   REGISTER_SCLKDIV: profiles[i].sclk_cycles <= reg_if.mask_write_bytes(profiles[i].sclk_cycles);
                   REGISTER_STARTWAIT: profiles[i].wait_start <=  reg_if.mask_write_bytes(profiles[i].wait_start);
                   REGISTER_CSNTOSCLK: profiles[i].csn_to_sclk_cycles <= reg_if.mask_write_bytes(profiles[i].csn_to_sclk_cycles);
                   REGISTER_SCLKTOCSN: profiles[i].sclk_to_csn_cycles <= reg_if.mask_write_bytes(profiles[i].sclk_to_csn_cycles);
                   REGISTER_XFERLEN: profiles[i].xfer_len <= reg_if.mask_write_bytes(profiles[i].xfer_len);
                   default: begin end                          
                 endcase
              end
           end
      end
   endgenerate

   assign error_clear = reg_if.is_reg_write(REGISTER_CTRLSTAT) & csr.wdata[1] & csr.wstrb[0];

   // Control Status
   always @(posedge csr.aclk)
     begin
        if (~csr.aresetn) begin
           autoinc_id <= 1'b0;
           engine_enable <= 1'b0;
        end else if (reg_if.is_reg_write(REGISTER_CTRLSTAT)) begin
           if (csr.wstrb[0]) begin
              engine_enable <= csr.wdata[0];
              autoinc_id <= csr.wdata[3];
           end
        end
     end

   
   always @(posedge csr.aclk)
     begin
        if (~csr.aresetn) begin
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



   assign cmd_stream.cmd.cpol = profiles[profile_sel].cpol;
   assign cmd_stream.cmd.cpha = profiles[profile_sel].cpha;
   assign cmd_stream.cmd.id = cmd_id;
   assign cmd_stream.cmd.device = device_sel;
   assign cmd_stream.cmd.sclk_cycles = profiles[profile_sel].sclk_cycles;
   assign cmd_stream.cmd.wait_start = profiles[profile_sel].wait_start;
   assign cmd_stream.cmd.csn_to_sclk_cycles = profiles[profile_sel].csn_to_sclk_cycles;
   assign cmd_stream.cmd.sclk_to_csn_cycles = profiles[profile_sel].sclk_to_csn_cycles;
   assign cmd_stream.cmd.xfer_len = profiles[profile_sel].xfer_len;

   logic cmd_trigger, cmd_is_busy;
   
   always @(posedge csr.aclk)
     begin
        cmd_trigger = reg_if.is_reg_write(REGISTER_TRIGGER);
        cmd_is_busy = (cmd_stream.cmd_valid & ~cmd_stream.cmd_ready);
        cmd_do_issue = cmd_trigger & ~cmd_is_busy;
        
        if (~reg_if.aresetn | ~cmd_stream.aresetn) begin
            cmd_stream.cmd_valid = 1'b0;
            cmd_failed_issue = 1'b0;
        end else if (cmd_trigger) begin
            if (cmd_do_issue) begin
                cmd_stream.cmd_valid = 1'b1;
            end else begin
                cmd_failed_issue = 1;
            end
        end else begin
            cmd_failed_issue = reg_if.is_reg_read(REGISTER_TRIGGER) ? 0 : cmd_failed_issue;
            cmd_stream.cmd_valid = cmd_stream.cmd_valid & ~cmd_stream.cmd_ready;
        end
    end

   
   always @( posedge csr.aclk )
     begin
        if (~csr.aresetn) begin
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
   logic   read_miso;
   
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
               reg_if.rreg_data <= { {{CSR_DATA_WIDTH-2}{1'b0}}, read_profile.cpol, read_profile.cpha };
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
             REGISTER_TRIGGER: reg_if.rreg_data <= { cmd_failed_issue, cmd_stream.cmd_ready };
             REGISTER_MOSIFIFO: reg_if.rreg_data <= mosi_read_data;
             REGISTER_MISOFIFO: reg_if.rreg_data <= axis_miso.tvalid ? axis_miso.tdata : {{CSR_DATA_WIDTH}{1'b1}};
             REGISTER_TRIGGER: reg_if.rreg_data <= { {{CSR_DATA_WIDTH-2}{1'b0}}, cmd_failed_issue, cmd_stream.cmd_ready};
             default: reg_if.rreg_data <= 0;
           endcase
        end
     end
endmodule
