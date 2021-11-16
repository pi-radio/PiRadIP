`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 11/05/2021 04:31:09 PM
// Design Name: 
// Module Name: piradma_mm2s_gather
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

module piradip_ring_buffer #(
        parameter integer CNTBITS = 2,
        localparam integer CNT = (1 << CNTBITS)
    ) (
        input logic clk,
        input logic rstn,
        output logic [CNTBITS-1:0] head,
        output logic [CNTBITS-1:0] tail,
        output logic empty,
        output logic full
    );

    assign empty = (head == tail);
    assign full = (head == tail + 1);

    always @(posedge clk)
    begin
        if (~rstn) begin
            head = 0;
            tail = 0;
        end
    end

    function push();
        head <= head + 1;
    endfunction;

    function pop();
        tail <= tail + 1;
    endfunction;
endmodule

module piradma_mm2s_gather #(
    ) (
        axis_simple fetch_out,
        axis_simple descriptor_in,
        axis_simple address_out,
        axis_simple read_op_in
    );
    
    logic rstn;
    
    assign rstn = fetch_out.aresetn & descriptor_in.aresetn & address_out.aresetn & read_op_in.aresetn;
    
    localparam DESC_WORD_WIDTH=descriptor_in.WIDTH;
    
    typedef logic [DESC_WORD_WIDTH-1:0] desc_word_t;
    
    typedef struct packed {
        desc_word_t base;
        desc_word_t len;
        desc_word_t flags;
        desc_word_t extra;
    } descriptor_t;

    localparam NDESC_BITS=2;
    localparam NDESC=(1 << NDESC_BITS);
    
    piradip_ring_buffer #(
        .CNTBITS(NDESC_BITS)
    ) desc_cache (
        .clk(descriptor_in.aclk),
        .rstn(rstn)
    );
    
    descriptor_t desc[NDESC];

    
    typedef enum {
        DESC_STATE_BASE = 0,
        DESC_STATE_LEN,
        DESC_STATE_FLAGS,
        DESC_STATE_EXTRA,
        DESC_STATE_WAIT_POP
    } desc_state_t;
    
    desc_state_t desc_state;
    
    always @(descriptor_in.aclk)
    begin
        if (~rstn) begin
        end else begin
            // if (done with descriptor) pop()
            
            descriptor_in.tready <= ~(desc_state == DESC_STATE_WAIT_POP);
            
            case (desc_state)
            DESC_STATE_BASE:
                if (descriptor_in.tready & descriptor_in.tvalid) begin
                    desc[desc_cache.tail].base <= decriptor_in.tdata;
                    desc_state <= DESC_STATE_LEN;
                end
            DESC_STATE_LEN:
                if (descriptor_in.tready & descriptor_in.tvalid) begin
                    desc[desc_cache.tail].len <= decriptor_in.tdata;
                    desc_state <= DESC_STATE_FLAGS;
                end
            DESC_STATE_FLAGS:
                if (descriptor_in.tready & descriptor_in.tvalid) begin
                    desc[desc_cache.tail].flags <= decriptor_in.tdata;
                    desc_state <= DESC_STATE_EXTRA;
                end
            DESC_STATE_EXTRA:
                if (descriptor_in.tready & descriptor_in.tvalid) begin
                    desc[desc_cache.tail].extra <= decriptor_in.tdata;
                    if (desc_queue.full) begin
                        desc_state <= DESC_STATE_WAIT_POP;
                    end else begin
                        desc_queue.push();
                        desc_state <= DESC_STATE_BASE;
                    end
                end
            DESC_STATE_WAIT_POP:
                    if (desc_queue.full) begin
                        desc_state <= DESC_STATE_WAIT_POP;
                    end else begin
                        desc_queue.push();
                        desc_state <= DESC_STATE_BASE;
                    end
            endcase
            
        end
    end
    
endmodule
