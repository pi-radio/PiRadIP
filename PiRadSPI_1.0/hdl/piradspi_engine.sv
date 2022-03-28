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
`include "piradspi.svh"
        
module piradspi_fifo_engine #(
	    parameter integer SEL_MODE        = 1,
        parameter integer SEL_WIDTH       = 8,
        parameter integer CMD_FIFO_DEPTH  = 16,
        parameter integer DATA_FIFO_DEPTH = 64
    ) (
        input logic clk,
        input logic rstn,
        
        axis_simple axis_cmd,
        axis_simple axis_mosi,
        axis_simple axis_miso,
        
        output logic cmd_completed,
        output logic engine_error,
        output logic engine_busy,
        
        output logic sclk,
        output logic mosi,
        input logic miso,
        output logic [SEL_WIDTH-1:0] csn,
        output logic sel_active
    );

    import piradspi::*;

    axis_simple #(.WIDTH(CMD_FIFO_WIDTH)) f2e_cmd();
    axis_simple #(.WIDTH(axis_mosi.WIDTH)) f2e_mosi();
    axis_simple #(.WIDTH(axis_miso.WIDTH)) e2f_miso();

    piradspi_engine #(
	    .SEL_MODE(SEL_MODE),
        .SEL_WIDTH(SEL_WIDTH)
    ) engine (
        .clk(clk),
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .sel_active(sel_active),
        .csn(csn),
        .cmd_completed(cmd_completed),
        .engine_error(engine_error),
        .engine_busy(engine_busy),
        .axis_cmd(f2e_cmd.SUBORDINATE),
        .axis_mosi(f2e_mosi.SUBORDINATE),
        .axis_miso(e2f_miso.MANAGER)
    );

    piradip_axis_fifo_sss #(
        .DEPTH(CMD_FIFO_DEPTH)
    ) cmd_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(axis_cmd),
        .m_axis(f2e_cmd.MANAGER)
    );

    piradip_axis_fifo_sss #(
        .DEPTH(DATA_FIFO_DEPTH)
    ) mosi_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(axis_mosi),
        .m_axis(f2e_mosi.MANAGER)
    );
    
    piradip_axis_fifo_sss #(
        .DEPTH(DATA_FIFO_DEPTH)
    ) miso_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(e2f_miso.SUBORDINATE),
        .m_axis(axis_miso)
    );


endmodule

module piradspi_engine #(
	    parameter integer SEL_MODE        = 1,
        parameter integer SEL_WIDTH       = 8
    ) (
        input clk,
        input rstn,
        
        axis_simple axis_cmd,
        axis_simple axis_mosi,
        axis_simple axis_miso,
        
        output wire cmd_completed,
        output logic engine_error,
        output logic engine_busy,
        
        output wire sclk,
        output wire mosi,
        input wire miso,
        output reg [SEL_WIDTH-1:0] csn,
        output reg sel_active
    );
    import piradspi::*;

    localparam DATA_FIFO_WIDTH = axis_mosi.WIDTH;
    localparam BIT_COUNT_WIDTH = $clog2(DATA_FIFO_WIDTH+1);
    localparam RESPONSE_PAD_WIDTH = DATA_FIFO_WIDTH-MAGIC_WIDTH-CMD_ID_WIDTH;
    
    typedef logic [DATA_FIFO_WIDTH-1:0] data_word_t;

    typedef union packed {
        struct packed {
        response_t resp;
        logic [RESPONSE_PAD_WIDTH-1:0] pad;
        } r;
        logic [DATA_FIFO_WIDTH-1:0] data;
    } response_u_t;

    command_u_t pending_cmd;   
    command_t cur_cmd;
     
    assign pending_cmd.data = axis_cmd.tdata; 
      
    function logic [SEL_WIDTH-1:0] gen_sel(input int sel_mode, input int device);
        if (sel_mode == 0) begin
            return 1 << device;
        end else begin
            return device;
        end
    endfunction
        
    reg sclk_gen;
    wait_t sclk_cnt;
    assign sclk = sclk_gen ^ cur_cmd.cpol;

    response_u_t cur_data_out;
        
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
    xfer_len_t xfer_bits;
    
    piradip_state_timer state_timer(
        .rstn(rstn), 
        .clk(clk), 
        .state(state), 
        .cycles(state_cycles), 
        .trigger(state_trigger));

    wire sclk_hold; // Stretch SCLK to deal with flow control axis_cmd2 axis_cmd
    wire consume_cmd;
    
    wire mosi_bit_empty;
    wire miso_bit_full;
     
    assign consume_cmd = axis_cmd.tready & axis_cmd.tvalid;

    piradip_bit_stream mosi_stream(.clk(clk), .resetn(rstn));
    piradip_bit_stream miso_stream(.clk(clk), .resetn(rstn));

    //axis_simple mosi_words(.clk(clk), .rstn(rstn));
    //axis_simple miso_words(.clk(clk), .rstn(rstn));
    
    piradip_stream_to_bit #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) mosi_shift_reg(
        .clk(clk), 
        .rstn(rstn),
        .align(cmd_completed),
        .empty(mosi_bit_empty),
        .bits_out(mosi_stream.MANAGER),
        .words_in(axis_mosi)
    );

    piradip_bit_to_stream #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) miso_shift_reg(
        .clk(clk), 
        .rstn(rstn),
        .align(cmd_completed),
        .full(miso_bit_full),
        .bits_in(miso_stream.SUBORDINATE),
        .words_out(axis_miso)
    );

    assign mosi = mosi_stream.tdata;
    assign miso_stream.tdata = miso;
    assign cmd_completed = (state == END_CMD);
    
    assign cur_data_out.r.resp.magic = RESPONSE_MAGIC;
    assign cur_data_out.r.resp.id = pending_cmd.c.cmd.id;
    assign cur_data_out.r.pad = 0;
    
    assign sclk_hold = (mosi_stream.tready & ~mosi_stream.tvalid) || (~miso_stream.tready & miso_stream.tvalid);

    always @(posedge clk)
    begin
        if (~rstn) begin
            mosi_stream.tready <= 1'b0;
        end else if (mosi_stream.tready) begin
            // If we're here, this means we're waiting on a bit, so if we got one, great!
            if (mosi_stream.tvalid) begin
                mosi_stream.tready <= 1'b0;
            end
            // If not, well, we keep waiting
        end else if ((state == LATCH) && (sclk_cnt == 0)) begin
            mosi_stream.tready <= 1'b1;
        end
    end

    always_comb engine_busy = (state != IDLE);
    always_comb engine_error = 0;

    always @(posedge clk)
    begin
        if (~rstn) begin
            csn <= 0;
            sel_active <= 1'b0;
            state <= IDLE;
            cur_cmd.cpol <= 1'b0;
            cur_cmd.cpha <= 1'b0;
            axis_cmd.tready <= 1'b0;
            miso_stream.tvalid <= 1'b0;
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
                        axis_cmd.tready <= 1'b0;
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
                        axis_cmd.tready <= ~mosi_bit_empty & axis_miso.tready;
                    end
                end
                
                WAIT_BEGIN_CMD: begin                   
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
                    if (state_trigger) begin
                        if (cur_cmd.cpha == 1) begin
                            state <= SHIFT;
                        end else begin
                            miso_stream.tvalid <= 1'b1;
                            state <= LATCH;
                        end
                        
                        sclk_gen <= ~sclk_gen;
                    end else begin
                        state <= SELECT_DEVICE;
                    end
                end
                
                LATCH: begin
                    if (miso_stream.tvalid & miso_stream.tready) begin
                        miso_stream.tvalid <= 1'b0;
                    end
                    
                    if (sclk_cnt != 0) begin
                        sclk_cnt <= sclk_cnt - 1;
                    end else if (~sclk_hold) begin
                        if (cur_cmd.cpha == 1 && xfer_bits == 0) begin
                            state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                            state <= DESELECT_DEVICE;                           
                        end else begin
                            sclk_cnt <= cur_cmd.sclk_cycles;
                            sclk_gen <= ~sclk_gen;
                            state <= SHIFT;
                        end
                    end
                end
                
                SHIFT: begin
                    if (sclk_cnt != 0) begin
                        sclk_cnt <= sclk_cnt - 1;
                    end else if (~sclk_hold) begin
                        if (cur_cmd.cpha == 0 && xfer_bits == 1) begin
                            state_cycles <= pending_cmd.c.cmd.sclk_to_csn_cycles;
                            state <= DESELECT_DEVICE;
                        end else begin
                            xfer_bits <= xfer_bits - 1;
                            miso_stream.tvalid <= 1'b1;
                            sclk_cnt <= cur_cmd.sclk_cycles;
                            sclk_gen <= ~sclk_gen;
                            state <= LATCH;
                        end
                    end
                end
                                
                DESELECT_DEVICE: begin
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
