`timescale 1ns / 1ps

interface piradip_register_if #(
                                parameter integer DATA_WIDTH = 32,
                                parameter integer REGISTER_ADDR_BITS = 8
                                )(
                                  input aclk,
                                  input aresetn
                                  );

   localparam integer                   STRB_WIDTH=DATA_WIDTH/8;
   
   typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;

   logic                                  wren;
   regno_t wreg_no;
   logic [DATA_WIDTH-1:0]                 wreg_data;
   logic [STRB_WIDTH-1:0]                 wstrb;
   logic                                  rden;
   regno_t rreg_no;
   logic [DATA_WIDTH-1:0]                 rreg_data;       
   
   function automatic logic is_reg_read(input regno_t regno);
      return rden & (rreg_no == regno);
   endfunction;

   function automatic logic is_reg_write(input regno_t regno);
      return wren & (wreg_no == regno);
   endfunction;

   function automatic logic reg_update_bit(input regno_t regno, input integer bitno, input logic v);
      return (wren & (wreg_no == regno) && (wstrb[bitno/8] == 1)) ? wreg_data[bitno] : v;
   endfunction;

   function automatic logic is_reg_bit_set(input regno_t regno, input integer bitno);
      return wren & (wreg_no == regno) && (wreg_data & (1 << bitno)) && (wstrb[bitno/8] == 1);
   endfunction;

   function automatic logic [DATA_WIDTH-1:0] mask_write_bytes(input logic [DATA_WIDTH-1:0] r);
      integer                             i;
      logic [DATA_WIDTH-1:0]              retval;;
      for ( i = 0; i < STRB_WIDTH; i = i+1 ) begin
         retval[(i*8) +: 8] = wstrb[i] ? wreg_data[(i*8) +: 8] : r[(i*8) +: 8];
      end
      return retval;
   endfunction   

   modport CLIENT(import is_reg_read, is_reg_write, reg_update_bit, is_reg_bit_set, mask_write_bytes,
                  input wren, wreg_no, wreg_data, wstrb, 
                  rden, rreg_no, aclk, aresetn, 
                  output rreg_data);
   modport SERVER(output wren, wreg_no, wreg_data, wstrb, rden, rreg_no, 
                  input rreg_data, aclk, aresetn);

endinterface

module piradip_axi4mmlite_subordinate (
                                       axi4mm_lite.SUBORDINATE aximm,
                                       piradip_register_if.SERVER reg_if
                                       );
   import piradip_axi4::*;

   localparam integer DATA_WIDTH = $bits(aximm.data_t);
   localparam integer ADDR_WIDTH = $bits(aximm.addr_t);
   localparam integer ADDR_LSB = (DATA_WIDTH/32) + 1;
   localparam integer REGISTER_ADDR_BITS = ADDR_WIDTH - ADDR_LSB;
   
   
   logic              aw_en;
   logic [ADDR_WIDTH-1:0] awaddr_r;
   logic [ADDR_WIDTH-1:0] araddr_r;
   
   assign reg_if.rden = aximm.arready & aximm.arvalid & ~aximm.rvalid;

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

module piradip_register_to_stream #(
                            parameter DATA_WIDTH = 32,
                            parameter REGISTER_NO = 0
                            ) (
                               output logic                  do_issue,
                               output logic                  failed_issue,
                               output logic [DATA_WIDTH-1:0] read_data,
                               piradip_register_if.CLIENT reg_if,
                               axi4s.MANAGER stream
                               );
   logic                                                     busy;

   assign busy = (stream.tvalid & ~stream.tready);
   assign read_data = { failed_issue, stream.tready };

   always @(posedge reg_if.aclk)
     begin
        stream.tlast <= 1'b0;

        if (~reg_if.aresetn | ~stream.aresetn) begin
           stream.tvalid <= 1'b0;
           failed_issue <= 1'b0;
        end else if (reg_if.is_reg_write(REGISTER_NO)) begin
           if (~busy) begin
              stream.tvalid <= 1'b1;
              stream.tdata <= reg_if.wreg_data;
           end else begin
              failed_issue <= 1;
           end
        end else begin
           failed_issue <= reg_if.is_reg_read(REGISTER_NO) ? 0 : failed_issue;
           stream.tvalid <= stream.tvalid & ~stream.tready;
        end
     end

endmodule
