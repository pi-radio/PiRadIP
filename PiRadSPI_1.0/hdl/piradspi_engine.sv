`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/14/2021 11:40:11 AM
// Design Name: 
// Module Name: piradspi_engine
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

class piradspi_types #(parameter integer REG_WIDTH       = 32,
        parameter integer WAIT_WIDTH      = 8,
        parameter integer ID_WIDTH        = 8,
        parameter integer XFER_LEN_WIDTH  = 16,
        parameter integer DEVICE_ID_WIDTH = 8,
        parameter integer CMD_FIFO_DEPTH  = 16,
        parameter integer DATA_FIFO_DEPTH = 64,
        parameter integer DATA_FIFO_WIDTH = 32,
        parameter integer MAGIC_WIDTH     = 8);
    
    localparam RESPONSE_MAGIC = 8'hAD;    
    localparam RESPONSE_PAD_WIDTH=DATA_FIFO_WIDTH-MAGIC_WIDTH-ID_WIDTH;
    localparam BIT_COUNT_WIDTH = $clog2(DATA_FIFO_WIDTH+1);
    
    typedef logic [BIT_COUNT_WIDTH-1:0] bit_count_t;
              
    typedef struct packed {
        logic cpol;
        logic cpha;
        logic [ID_WIDTH-1:0] id;
        logic [DEVICE_ID_WIDTH-1:0] device;
        logic [WAIT_WIDTH-1:0] sclk_cycles;
        logic [WAIT_WIDTH-1:0] wait_start;
        logic [WAIT_WIDTH-1:0] csn_to_sclk_cycles;
        logic [WAIT_WIDTH-1:0] sclk_to_csn_cycles;        
        logic [XFER_LEN_WIDTH-1:0] xfer_len;
    } command_t;

    localparam CMD_FIFO_WIDTH = 8*($bits(command_t)/8 + (($bits(command_t) & 3'h7) ? 1 : 0));    
    
    //$error("CMD_FIFO_WIDTH: %d bits: %d\n", CMD_FIFO_WIDTH, $bits(command_t));
        
    typedef struct packed {
        logic [MAGIC_WIDTH-1:0]        magic;
        logic [ID_WIDTH-1:0]           id;
        logic [RESPONSE_PAD_WIDTH-1:0] pad; 
    } response_t;
    
    typedef union packed {
        struct packed {
            logic [CMD_FIFO_WIDTH-$bits(command_t)-1:0] pad;
            command_t cmd;
        } c;
        logic [CMD_FIFO_WIDTH-1:0] data;
    } command_u_t;
       
    typedef union packed {
        response_t resp;
        logic [DATA_FIFO_WIDTH-1:0] data;
    } response_u_t;
        
endclass

module piradip_state_timer #(parameter integer REG_WIDTH=32) (
    input wire rstn,
    input wire clk,
    input wire [REG_WIDTH-1:0] state,
    input wire [REG_WIDTH-1:0] cycles,
    output wire trigger
);
    reg [REG_WIDTH-1:0] old_state;
    reg [REG_WIDTH-1:0] counter;
    
    assign trigger = ((state == old_state) && (counter == 0)) || ((state != old_state) && (cycles == 0));
    
    always @(posedge clk)
    begin
        if (~rstn) begin
            counter <= 0;
            old_state <= 0;                
        end else begin
            old_state <= state;
            if (state != old_state) begin
                counter <= (cycles > 0) ? cycles - 1 : 0;
            end else if (counter > 0) begin
                counter <= counter - 1;
            end
        end
    end
endmodule

module piradspi_engine #(
        type types = piradspi_types,
	    parameter integer SEL_MODE        = 1,
        parameter integer SEL_WIDTH       = 8,
        
        parameter integer DATA_FIFO_DEPTH = 32
    ) (
        input clk,
        input rstn,
        
        output wire sclk,
        output wire mosi,
        input wire miso,
        output reg [SEL_WIDTH-1:0] csn,
        output reg sel_active,
         
        input wire cmd_valid,
        output reg cmd_ready,
        input wire [types::CMD_FIFO_WIDTH-1:0] cmd_data,
        input wire cmd_tlast,
        output wire cmd_completed,
        
        input wire mosi_valid,
        output wire mosi_ready,
        input wire [types::DATA_FIFO_WIDTH-1:0] mosi_data,
        input wire mosi_tlast,
        
        output reg miso_valid,
        input wire miso_ready,
        output wire [types::DATA_FIFO_WIDTH-1:0] miso_data,
        output reg miso_tlast
    );
     
    types::command_u_t pending_cmd;   
    types::command_t cur_cmd;
     
    assign pending_cmd.data = cmd_data; 
      
    function logic [SEL_WIDTH-1:0] gen_sel(input int sel_mode, input int device);
        if (sel_mode == 0) begin
            return 1 << device;
        end else begin
            return device;
        end
    endfunction
        
    reg sclk_gen;
    reg [types::WAIT_WIDTH-1:0] sclk_cnt;
    assign sclk = sclk_gen ^ cur_cmd.cpol;

    typedef types::response_u_t response_u_t;

    wire response_u_t cur_data_out;
        
    typedef enum {
        IDLE = 0,
        FETCH1,
        WAIT_BEGIN_CMD,
        SELECT_DEVICE,
        LATCH,
        SHIFT,
        DESELECT_DEVICE,
        WAIT_END_CMD,
        END_CMD
    } state_t;    
    
    state_t state, last_state;

    reg [31:0] state_cycles;
    wire state_trigger;
    reg [types::XFER_LEN_WIDTH-1:0] xfer_bits;
    
    piradip_state_timer state_timer(
        .rstn(rstn), 
        .clk(clk), 
        .state(state), 
        .cycles(state_cycles), 
        .trigger(state_trigger));

    wire consume_cmd;
    
    assign consume_cmd = cmd_ready & cmd_valid;
    
    wire mosi_align, mosi_bit_valid, mosi_bit_data, mosi_bit_empty;
    reg mosi_bit_ready;
    
    reg mosi_bit_read;
    
    always @(posedge clk) mosi_bit_read = mosi_bit_ready & mosi_bit_valid;
    
    assign mosi = mosi_bit_data;
    
    assign mosi_align = state == END_CMD;
        
    piradip_stream_to_bit #(
        .WIDTH(types::DATA_FIFO_WIDTH)
    ) mosi_shift_reg(
        .clk(clk), 
        .rstn(rstn),
        .align(mosi_align),
        .empty(mosi_bit_empty),
        .bit_ready(mosi_bit_ready),
        .bit_valid(mosi_bit_valid),
        .bit_data(mosi_bit_data),
        .word_ready(mosi_ready),
        .word_data(mosi_data),
        .word_valid(mosi_valid)        
    );

    wire miso_align, miso_bit_full;
    wire miso_bit_ready;
    reg miso_bit_valid;
    
    assign miso_align = (state == END_CMD);
 
    wire miso_words_ready, miso_words_valid;
    wire [types::DATA_FIFO_WIDTH-1:0] miso_words_data;
    
    piradip_bit_to_stream #(
        .WIDTH(types::DATA_FIFO_WIDTH)
    ) miso_shift_reg(
        .clk(clk), 
        .rstn(rstn),
        .align(miso_align),
        .full(miso_bit_full),
        .bit_ready(miso_bit_ready),
        .bit_valid(miso_bit_valid),
        .bit_data(miso),
        .word_ready(miso_words_ready),
        .word_data(miso_words_data),
        .word_valid(miso_words_valid)        
    );

    assign miso_words_ready = ~consume_cmd & miso_ready;
    
    assign miso_data = consume_cmd ? cur_data_out.data : miso_words_data;
    assign miso_valid = consume_cmd ? 1'b1 : miso_words_valid;
    
    assign cur_data_out.resp.magic = types::RESPONSE_MAGIC;
    assign cur_data_out.resp.id = pending_cmd.c.cmd.id;
    assign cur_data_out.resp.pad = 0;

    assign cmd_completed = (state == END_CMD);

    wire sclk_hold;
    
    assign sclk_hold = (mosi_bit_ready & ~mosi_bit_valid) || (~miso_bit_ready & miso_bit_valid);

    always @(posedge clk)
    begin
        if (~rstn) begin
            csn <= 0;
            sel_active <= 1'b0;
            state <= IDLE;
            cur_cmd.cpol <= 1'b0;
            cur_cmd.cpha <= 1'b0;
            cmd_ready <= 1'b0;
            mosi_bit_ready <= 1'b0;
            miso_bit_valid <= 1'b0;
            xfer_bits <= 0;
        end else begin
            last_state <= state;
            
            case (state)
                IDLE: begin
                    sclk_gen <= 1'b0;
                    sel_active <= 1'b0;
                    csn <= 0;
                    
                    if (consume_cmd) begin                    
                        // Register command
                        cmd_ready <= 1'b0;
                        cur_cmd <= pending_cmd.c.cmd;
                        state_cycles <= pending_cmd.c.cmd.wait_start;
                        sclk_cnt <= pending_cmd.c.cmd.sclk_cycles;
                        xfer_bits <= pending_cmd.c.cmd.xfer_len;
                        
                        if (pending_cmd.c.cmd.wait_start) begin
                            state <= WAIT_BEGIN_CMD;
                        end else begin
                            state <= SELECT_DEVICE;
                        end
                    end else begin
                        state <= IDLE;
                        cmd_ready <= ~mosi_bit_empty & miso_ready;
                    end
                end
                
                WAIT_BEGIN_CMD: begin                   
                    miso_valid <= 1'b0;
                    if (state_trigger) begin
                        csn <= gen_sel(SEL_MODE, cur_cmd.device);
                        sel_active <= 1'b1;
                        state <= SELECT_DEVICE;
                        state_cycles <= cur_cmd.csn_to_sclk_cycles;
                    end else begin
                        state <= WAIT_BEGIN_CMD;
                    end
                end
                
                SELECT_DEVICE: begin
                    miso_valid <= 1'b0;
                    if (state_trigger) begin
                        if (cur_cmd.cpha == 1) begin
                            state <= SHIFT;
                        end else begin
                            miso_bit_valid <= 1'b1;
                            state <= LATCH;
                        end
                        
                        sclk_gen <= ~sclk_gen;
                    end else begin
                        state <= SELECT_DEVICE;
                    end
                end
                
                LATCH: begin
                    if (miso_bit_valid & miso_bit_ready) begin
                        miso_bit_valid <= 1'b0;
                    end
                    
                    if (sclk_cnt != 0) begin
                        sclk_cnt <= sclk_cnt - 1;
                    end else if (~sclk_hold) begin
                        if (cur_cmd.cpha == 1 && xfer_bits == 0) begin
                            mosi_bit_ready <= 1'b1;
                            state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                            state <= DESELECT_DEVICE;                           
                        end else begin
                            mosi_bit_ready <= 1'b1;
                            sclk_cnt <= cur_cmd.sclk_cycles;
                            sclk_gen <= ~sclk_gen;
                            state <= SHIFT;
                        end
                    end
                end
                
                SHIFT: begin
                    if (mosi_bit_ready & mosi_bit_valid) begin
                        mosi_bit_ready <= 1'b0;
                    end
                    
                    if (sclk_cnt != 0) begin
                        sclk_cnt <= sclk_cnt - 1;
                    end else if (~sclk_hold) begin
                        if (cur_cmd.cpha == 0 && xfer_bits == 1) begin
                            state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                            state <= DESELECT_DEVICE;
                        end else begin
                            xfer_bits <= xfer_bits - 1;
                            miso_bit_valid <= 1'b1;
                            sclk_cnt <= cur_cmd.sclk_cycles;
                            sclk_gen <= ~sclk_gen;
                            state <= LATCH;
                        end
                    end
                end
                                
                DESELECT_DEVICE: begin
                    mosi_bit_ready <= 1'b0;
                    if (state_trigger) begin
                        state <= WAIT_END_CMD;
                    end
                end
                
                WAIT_END_CMD: begin
                    sel_active <= 1'b0;
                    csn <= 0;
                    state <= END_CMD;
                end
                
                END_CMD: begin
                    state <= IDLE;
                end
            endcase
        end
    end
  
    
    
endmodule
