`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/05/2021 04:31:09 PM
// Design Name: 
// Module Name: piradma_mm2s_aximm_master
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module piradma_mm2s_aximm_manager(
        axi4mm aximm
    );
    
    localparam ADDR_WIDTH=aximm.ADDR_WIDTH;
    localparam DATA_WIDTH=aximm.DATA_WIDTH;
    
    localparam ARSIZE = (aximm.DATA_WIDTH == 4) ? AXI_SIZE_4 :
        (aximm.DATA_WIDTH == 8) ? AXI_SIZE_8 : 
        AXI_SIZE_1;
    
    typedef logic [ADDR_WIDTH-1:0] addr_t;
    typedef logic [DATA_WIDTH-1:0] data_t;
    
    typedef struct packed {
        bit valid;
        addr_t addr;
        addr_t len;
        axi_len_t cur_len;
    } pending_read_t;
    
    pending_read_t cur_read;
        
    typedef enum {
        AXIMM_READ_IDLE = 0,
        AXIMM_READ_GEN_ADDR,
        AXIMM_WAIT_READ_COMPLETE
    } aximm_read_state_t;
    
    aximm_read_state_t aximm_read_state;
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn || aximm_read_state != AXIMM_READ_GEN_ADDR) begin
            aximm.arid <= 0;
            aximm.araddr <= 0;
            aximm.arlen <= 0;
            aximm.arsize <= 0;
            aximm.arburst <= 0;
            aximm.arlock <= 0;
            aximm.arcache <= 0;
            aximm.arprot <= 0;
            aximm.arqos <= 0;
            aximm.arregion <= 0;
            aximm.aruser <= 0;
    
            aximm.arvalid <= 1'b0;
        end else begin
            aximm.arid <= 0;
            aximm.araddr <= cur_read.addr;
            aximm.arlen <= cur_read.cur_len;
            aximm.arsize <= ARSIZE;
            aximm.arburst <= AXI_BURST_INCR;
            aximm.arlock <= AXI_LOCK_NORMAL;
            aximm.arcache <= AXI_ARCACHE_WRITE_BACK_BOTH_ALLOCATE;
            aximm.arprot <= AXI_PROT_DATA;
            aximm.arqos <= AXI_QOS_DEFAULT;
            aximm.arregion <= AXI_REGION_DEFAULT;
            aximm.aruser <= 0;
        end    
    end
    
    always @(posedge aximm.aclk)
    begin
        aximm.arvalid <= (~aximm.aresetn) ? 1'b0 :
            (aximm.arvalid & aximm.arready) ? 1'b0 : 
            (aximm_read_state == AXIMM_READ_GEN_ADDR) ? 1'b1 : aximm.arvalid;
    end
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin

        end else begin
            case (aximm_read_state)
                AXIMM_READ_IDLE: begin
                   
                end
                
                AXIMM_READ_GEN_ADDR: begin
                    if (aximm.arvalid & aximm.arready) begin
                    end 
                end
                
                AXIMM_WAIT_READ_COMPLETE: begin
                end
                
                default: begin
                end
            endcase
        end                        
    end
endmodule
