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

interface piradspi_support #(
    type command_u_t,
    parameter CMD_FIFO_WIDTH=0
)();
    function automatic logic [CMD_FIFO_WIDTH-1:0]  build_command(
        input int dev,
        input int xfer_len,
        input int cmd_id,
        input logic cpol, 
        input logic cpha, 
        input int sclk_cycles=1,
        input int wait_start=1,
        input int csn_to_sclk_cycles = 5,
        input int sclk_to_csn_cycles = 5
        );
        
        command_u_t cmd;
        
        cmd.c.cmd.id = cmd_id;
        cmd.c.cmd.cpol = cpol;
        cmd.c.cmd.cpha = cpha;
        
        cmd.c.cmd.device = dev;
        cmd.c.cmd.sclk_cycles = sclk_cycles;
        cmd.c.cmd.wait_start = wait_start;
        cmd.c.cmd.csn_to_sclk_cycles = csn_to_sclk_cycles;
        cmd.c.cmd.sclk_to_csn_cycles = sclk_to_csn_cycles;
        cmd.c.cmd.xfer_len = xfer_len;
        cmd.c.pad = 0;
        
        return cmd.data;
    endfunction              
endinterface

module piradspi_fifo_engine #(
        parameter integer WAIT_WIDTH      = 8,
        parameter integer CMD_ID_WIDTH    = 8,
        parameter integer XFER_LEN_WIDTH  = 16,
        parameter integer DEVICE_ID_WIDTH = 8,
        parameter integer MAGIC_WIDTH     = 8,
        parameter integer DATA_FIFO_WIDTH = 32,
	    parameter integer SEL_MODE        = 1,
        parameter integer SEL_WIDTH       = 8
    ) (
        input clk,
        input rstn,
        
        axis_simple axis_cmd,
        axis_simple axis_mosi,
        axis_simple axis_miso,
        
        output wire cmd_completed,
        
        output wire sclk,
        output wire mosi,
        input wire miso,
        output reg [SEL_WIDTH-1:0] csn,
        output reg sel_active
    );
    
    piradspi_engine #(
        .WAIT_WIDTH(WAIT_WIDTH),
        .CMD_ID_WIDTH(CMD_ID_WIDTH),
        .XFER_LEN_WIDTH(XFER_LEN_WIDTH),
        .DEVICE_ID_WIDTH(DEVICE_ID_WIDTH),
        .MAGIC_WIDTH(MAGIC_WIDTH),
        .DATA_FIFO_WIDTH(DATA_FIFO_WIDTH),
	    .SEL_MODE(SEL_MODE),
        .SEL_WIDTH(SEL_WIDTH)
    ) engine (
        .clk(clk_gen.clk),
        .rstn(rstn),
        .sclk(sclk),
        .mosi(mosi),
        .miso(miso),
        .sel_active(sel_active),
        .csn(chip_selects),
        .cmd_completed(cmd_completed),
        .axis_cmd(f2e_cmd.SLAVE),
        .axis_mosi(f2e_mosi.SLAVE),
        .axis_miso(e2f_miso.MASTER)
    );
    
    localparam CMD_FIFO_WIDTH = engine.CMD_FIFO_WIDTH;
    //piradspi_support support = engine.support;

    axis_simple #(.WIDTH(CMD_FIFO_WIDTH)) f2e_cmd();
    axis_simple #(.WIDTH(DATA_FIFO_WIDTH)) f2e_mosi();
    axis_simple #(.WIDTH(DATA_FIFO_WIDTH)) e2f_miso();


    piradip_axis_fifo_sss #(
        .WIDTH(CMD_FIFO_WIDTH)
    ) cmd_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(axis_cmd),
        .m_axis(f2e_cmd.MASTER)
    );

    piradip_axis_fifo_sss #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) mosi_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(axis_mosi),
        .m_axis(f2e_mosi.MASTER)
    );
    
    piradip_axis_fifo_sss #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) miso_fifo (
        .aclk(clk),
        .aresetn(rstn),
        .s_axis(e2f_miso.SLAVE),
        .m_axis(axis_miso)
    );


endmodule

module piradspi_engine #(
        parameter integer WAIT_WIDTH      = 8,
        parameter integer CMD_ID_WIDTH    = 8,
        parameter integer XFER_LEN_WIDTH  = 16,
        parameter integer DEVICE_ID_WIDTH = 8,
        parameter integer MAGIC_WIDTH     = 8,
        parameter integer DATA_FIFO_WIDTH = 32,
	    parameter integer SEL_MODE        = 1,
        parameter integer SEL_WIDTH       = 8
    ) (
        input clk,
        input rstn,
        
        axis_simple axis_cmd,
        axis_simple axis_mosi,
        axis_simple axis_miso,
        
        output wire cmd_completed,
        
        output wire sclk,
        output wire mosi,
        input wire miso,
        output reg [SEL_WIDTH-1:0] csn,
        output reg sel_active
    );
    
    localparam RESPONSE_MAGIC = 8'hAD;    
    localparam RESPONSE_PAD_WIDTH=DATA_FIFO_WIDTH-MAGIC_WIDTH-CMD_ID_WIDTH;
    localparam BIT_COUNT_WIDTH = $clog2(DATA_FIFO_WIDTH+1);

    typedef logic [WAIT_WIDTH-1:0] wait_t;          
    typedef logic [CMD_ID_WIDTH-1:0] cmd_id_t;
    typedef logic [XFER_LEN_WIDTH-1:0] xfer_len_t;
    typedef logic [DEVICE_ID_WIDTH-1:0] dev_id_t;
    typedef logic [MAGIC_WIDTH-1:0] magic_t;
    
    typedef struct packed {
        logic       cpol;
        logic       cpha;
        cmd_id_t    id;
        dev_id_t    device;
        wait_t      sclk_cycles;
        wait_t      wait_start;
        wait_t      csn_to_sclk_cycles;
        wait_t      sclk_to_csn_cycles;        
        xfer_len_t  xfer_len;
    } command_t;    
    
    localparam CMD_FIFO_WIDTH = 8*($bits(command_t)/8 + (($bits(command_t) & 3'h7) ? 1 : 0));

    
    typedef logic [CMD_FIFO_WIDTH-1:0] cmd_word_t;
    typedef logic [DATA_FIFO_WIDTH-1:0] data_word_t;


    typedef struct packed {
        magic_t        magic;
        cmd_id_t       id;
        logic [RESPONSE_PAD_WIDTH-1:0] pad; 
    } response_t;
    
    typedef union packed {
        struct packed {
            logic [CMD_FIFO_WIDTH-$bits(command_t)-1:0] pad;
            command_t cmd;
        } c;
        cmd_word_t data;
    } command_u_t;
 
        
    typedef union packed {
        response_t resp;
        logic [DATA_FIFO_WIDTH-1:0] data;
    } response_u_t;
    
    piradspi_support #(.command_u_t(command_u_t), .CMD_FIFO_WIDTH(CMD_FIFO_WIDTH)) support();
     
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

    wire consume_cmd;
    
    assign consume_cmd = axis_cmd.tready & axis_cmd.tvalid;
    
    wire mosi_align, mosi_bit_valid, mosi_bit_data, mosi_bit_empty;
    wire mosi_bit_ready;
    
    reg mosi_bit_read;
    
    always @(posedge clk) mosi_bit_read = mosi_bit_ready & mosi_bit_valid;
    
    assign mosi = mosi_bit_data;
    
    assign mosi_align = state == END_CMD;
        
    piradip_stream_to_bit #(
        .WIDTH(DATA_FIFO_WIDTH)
    ) mosi_shift_reg(
        .clk(clk), 
        .rstn(rstn),
        .align(mosi_align),
        .empty(mosi_bit_empty),
        .bit_ready(mosi_bit_ready),
        .bit_valid(mosi_bit_valid),
        .bit_data(mosi_bit_data),
        .word_ready(axis_mosi.tready),
        .word_data(axis_mosi.tdata),
        .word_valid(axis_mosi.tvalid)        
    );

    wire miso_align, miso_bit_full;
    wire miso_bit_ready;
    reg miso_bit_valid;
    
    assign miso_align = (state == END_CMD);
 
    wire miso_words_ready, miso_words_valid;
    wire [DATA_FIFO_WIDTH-1:0] miso_words_data;
    
    piradip_bit_to_stream #(
        .WIDTH(DATA_FIFO_WIDTH)
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

    assign miso_words_ready = ~consume_cmd & axis_miso.tready;
    
    assign axis_miso_data = consume_cmd ? cur_data_out.data : miso_words_data;
    assign axis_miso_valid = consume_cmd ? 1'b1 : miso_words_valid;
    
    assign cur_data_out.resp.magic = RESPONSE_MAGIC;
    assign cur_data_out.resp.id = pending_cmd.c.cmd.id;
    assign cur_data_out.resp.pad = 0;

    assign cmd_completed = (state == END_CMD);

    wire sclk_hold;
    
    assign sclk_hold = (mosi_bit_ready & ~mosi_bit_valid) || (~miso_bit_ready & miso_bit_valid);

    reg mosi_bit_complete;
    always @(posedge clk) mosi_bit_complete <= mosi_bit_valid & mosi_bit_ready;

    assign mosi_bit_ready = (~rstn) ? 1'b0 : 
        (mosi_bit_ready | ((state == LATCH) & ~(~miso_bit_ready & miso_bit_valid) & (sclk_cnt == 0))) & ~mosi_bit_complete;

    always @(posedge clk)
    begin
        if (~rstn) begin
            csn <= 0;
            sel_active <= 1'b0;
            state <= IDLE;
            cur_cmd.cpol <= 1'b0;
            cur_cmd.cpha <= 1'b0;
            axis_cmd.tready <= 1'b0;
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
                    axis_miso.tvalid <= 1'b0;
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
                    axis_miso.tvalid <= 1'b0;
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
                            miso_bit_valid <= 1'b1;
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
