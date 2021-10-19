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
        output wire cmd_ready,
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
    wire sclk_hold;
    assign sclk = sclk_gen ^ cur_cmd.cpol;

    types::response_u_t cur_data_out;
    
    assign miso_data = cur_data_out;
    
    typedef enum {
        IDLE = 0,
        FETCH1,
        WAIT_BEGIN_CMD,
        FIRST_SHIFT,
        SELECT_DEVICE,
        LATCH,
        SHIFT,
        LAST_LATCH,
        DESELECT_DEVICE,
        WAIT_END_CMD,
        END_CMD
    } state_t;    
    
    state_t state, last_state;

    reg [31:0] state_cycles;
    wire state_trigger;
    
    piradip_state_timer state_timer(
        .rstn(rstn), 
        .clk(clk), 
        .state(state), 
        .cycles(state_cycles), 
        .trigger(state_trigger));

    reg [types::DATA_FIFO_WIDTH-1:0] mosi_shift_reg;
    wire mosi_empty;
    wire consume_cmd;
    
    reg [7:0] mosi_bits_avail;
    
    assign mosi_empty = (mosi_bits_avail == 0);
    assign mosi_ready = mosi_empty;
    assign mosi_reload_ack = mosi_empty & mosi_valid;
    
    typedef enum logic [1:0] {
        PH_LATCH,
        PH_SHIFT,
        PH_NONE
    } phase_t;
    
    wire phase_t phase;
    
    assign phase = (state == last_state) ? PH_NONE :
                   (state == SHIFT) ? PH_SHIFT :
                   (state == FIRST_SHIFT || (cur_cmd.cpol == 0 && state == SELECT_DEVICE)) ? PH_SHIFT :
                   (state == LATCH) ? PH_LATCH :
                   PH_NONE;
    
    assign consume_cmd = cmd_ready & cmd_valid;
    assign mosi = (~rstn) ? 0 :
                  (phase == PH_SHIFT) ? mosi_shift_reg[types::DATA_FIFO_WIDTH-1] :
                  mosi;
                  
    /* MOSI shift register */
    always @(posedge clk)
    begin
        if (~rstn) begin
            mosi_bits_avail <= 0;
            mosi_shift_reg <= 0;
        end else begin
            if (mosi_empty & mosi_valid) begin
                mosi_shift_reg <= mosi_data;
                mosi_bits_avail <= types::DATA_FIFO_WIDTH;
            end else if (phase == PH_SHIFT) begin
                mosi_shift_reg <= { mosi_shift_reg[types::DATA_FIFO_WIDTH-2:0], 1'b0 };
                mosi_bits_avail <= mosi_bits_avail - 1;
            end else if (state == END_CMD) begin
                mosi_bits_avail <= 0;
            end
        end
    end
 
    always @(posedge clk)
    begin
        if (~rstn) begin
            cur_data_out.data <= 0;
            miso_valid <= 1'b0;
        end else begin
            if (state == IDLE && consume_cmd) begin
                cur_data_out.resp.magic = types::RESPONSE_MAGIC;
                cur_data_out.resp.id = pending_cmd.c.cmd.id;
                cur_data_out.resp.pad = 0;
                miso_valid <= 1'b1;
            end else if (phase == PH_SHIFT) begin
                cur_data_out.data = { cur_data_out.data[types::DATA_FIFO_WIDTH-2:0], 1'b0 };
            end else if (phase == PH_LATCH) begin
                cur_data_out.data = { cur_data_out.data[types::DATA_FIFO_WIDTH-1:1], miso };
            end
            
                
        end
    end

    assign cmd_completed = (state == END_CMD);
    assign cmd_ready = rstn & (state == IDLE) & (mosi_bits_avail > 0) & miso_ready;
    assign sclk_hold = (mosi_ready & ~mosi_valid);
        
    always @(posedge clk)
    begin
        if (~rstn) begin
            csn <= 0;
            sel_active <= 1'b0;
            state <= IDLE;
            cur_cmd.cpol <= 1'b0;
            cur_cmd.cpha <= 1'b0;           
            miso_valid <= 0;
            cur_data_out.data <= 0;
            miso_tlast <= 0;
        end else begin
            last_state <= state;
            
            case (state)
                IDLE: begin
                    sclk_gen <= 1'b0;
                    sel_active <= 1'b0;
                    csn <= 0;
                    
                    if (consume_cmd) begin                    
                        // Register command
                        cur_cmd <= pending_cmd.c.cmd;
                        state_cycles <= pending_cmd.c.cmd.wait_start;
                        sclk_cnt <= pending_cmd.c.cmd.sclk_cycles;
                        
                        if (pending_cmd.c.cmd.wait_start) begin
                            state <= WAIT_BEGIN_CMD;
                        end else begin
                            state <= SELECT_DEVICE;
                        end
                    end else begin
                        state <= IDLE;
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
                        cur_cmd.xfer_len <= cur_cmd.xfer_len - 1;
                        state <= cur_cmd.cpha ? FIRST_SHIFT : LATCH;
                        sclk_gen <= ~sclk_gen;
                    end else begin
                        state <= SELECT_DEVICE;
                    end
                end
                
                FIRST_SHIFT: begin
                    if (~sclk_hold & sclk_cnt == 0) begin
                        sclk_cnt <= cur_cmd.sclk_cycles;
                        sclk_gen <= ~sclk_gen;
                        state <= LATCH;
                    end else begin
                        sclk_cnt <= sclk_cnt - 1;
                    end
                end
                
                LATCH: begin
                    if (~sclk_hold & sclk_cnt == 0) begin
                        sclk_cnt <= cur_cmd.sclk_cycles;
                        sclk_gen <= ~sclk_gen;
                        state <= SHIFT;
                    end else begin
                        sclk_cnt <= sclk_cnt - 1;
                    end
                end
                
                SHIFT: begin
                    if (~sclk_hold & sclk_cnt == 0) begin
                        sclk_cnt <= cur_cmd.sclk_cycles;
                        sclk_gen <= ~sclk_gen;
                        cur_cmd.xfer_len <= cur_cmd.xfer_len - 1;
                        if (cur_cmd.xfer_len > 1) begin
                            state <= LATCH;
                        end else if (cur_cmd.cpha == 0) begin
                            state <= LAST_LATCH;
                        end else begin
                            state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                            state <= DESELECT_DEVICE;
                        end
                    end else begin
                        sclk_cnt <= sclk_cnt - 1;
                    end
                end
                
                LAST_LATCH: begin
                    if (sclk_cnt == 0) begin
                        sclk_gen <= ~sclk_gen;
                        state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                        state <= DESELECT_DEVICE;
                    end else begin
                        sclk_cnt <= sclk_cnt - 1;
                    end
                end
                
                DESELECT_DEVICE: begin
                    if (state_trigger) begin
                        state <= WAIT_END_CMD;
                    end
                end
                
                WAIT_END_CMD: begin
                    state <= END_CMD;
                end
                
                END_CMD: begin
                    state <= IDLE;
                end
            endcase
        end
    end
  
    
    
endmodule
