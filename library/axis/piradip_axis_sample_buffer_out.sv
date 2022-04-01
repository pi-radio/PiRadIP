`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 03/28/2022 03:41:23 PM
// Design Name: 
// Module Name: piradip_axis_sample_buffer_out
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


package piradip_sample_buffer;
    localparam REGISTER_CTRLSTAT = 0;
    
    localparam CTRLSTAT_ACTIVE         = 0;
    localparam CTRLSTAT_ONE_SHOT       = 1;
    
    localparam REGISTER_START_OFFSET = 1;
    localparam REGISTER_END_OFFSET  = 2;
endpackage

module piradip_axis_sample_buffer_csr #(
    parameter STREAM_OFFSET_WIDTH = 5,
    parameter DEBUG=1
) (
    axi4mm_lite.SUBORDINATE aximm,
    
    input logic trigger,
    input logic stream_clk,
    input logic stream_stopped,
    output logic stream_update,
    output logic stream_active,
    output logic stream_one_shot,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_start_offset,
    output logic [STREAM_OFFSET_WIDTH-1:0] stream_end_offset
);
    localparam DATA_WIDTH = $bits(aximm.rdata);
    localparam ADDR_WIDTH = $bits(aximm.araddr);
    localparam REGISTER_ADDR_BITS = ADDR_WIDTH-$clog2(DATA_WIDTH/8);

    import piradip_sample_buffer::*;

    logic mm_update;
    logic mm_active;
    logic mm_one_shot;
    logic [STREAM_OFFSET_WIDTH-1:0] mm_start_offset;
    logic [STREAM_OFFSET_WIDTH-1:0] mm_end_offset;

    localparam CDC_WIDTH = 2 + 2*STREAM_OFFSET_WIDTH;

    piradip_register_if #(
        .DATA_WIDTH(DATA_WIDTH), 
        .REGISTER_ADDR_BITS(REGISTER_ADDR_BITS)
    ) reg_if (
        .aclk(aximm.aclk), 
        .aresetn(aximm.aresetn)
    );

    piradip_axi4mmlite_subordinate 
        sub_imp(.reg_if(reg_if.SERVER), .aximm(aximm), .*);

    piradip_cdc_auto_word #(
        .WIDTH(2)
    ) ctrl_cdc (
        .rst(~aximm.aresetn),
        .src_clk(aximm.aclk),
        .src_data({ mm_one_shot, mm_active }),
        .src_send(mm_update),
        .dst_clk(stream_clk),
        .dst_data({ stream_one_shot, stream_active }),
        .dst_update(stream_update)        
    );
    
    piradip_cdc_auto_reg #(
        .WIDTH(2*STREAM_OFFSET_WIDTH)
    ) offset_cdc (
        .rst(~aximm.aresetn),
        .src_clk(aximm.aclk),
        .src_data({ mm_end_offset, mm_start_offset }),
        .dst_clk(stream_clk),
        .dst_data({ stream_end_offset, stream_start_offset})  
    );
    
    function automatic update_flag(ref logic flag, logic newval);
        if (flag != newval) begin
            flag = newval;
            mm_update = 1'b1;
        end
    endfunction
    
    logic initialized;
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            initialized = 1'b0;
            mm_update = 1'b0;
            mm_active = 1'b0;
            mm_one_shot = 1'b0;
            mm_start_offset = 0;
            mm_end_offset = {STREAM_OFFSET_WIDTH{1'b1}};
        end else begin
            mm_update = ~initialized;
            initialized = 1'b1;
            
            if (trigger) update_flag(mm_active, 1'b1);
            
            if(reg_if.wren) begin
                case (reg_if.wreg_no)
                REGISTER_CTRLSTAT: begin
                    if (reg_if.wstrb[0]) begin
                        update_flag(mm_active, reg_if.wreg_data[CTRLSTAT_ACTIVE]);
                        update_flag(mm_one_shot, reg_if.wreg_data[CTRLSTAT_ONE_SHOT]);
                    end
                end
                REGISTER_START_OFFSET: 
                    mm_start_offset = reg_if.mask_write_bytes(mm_start_offset);
                REGISTER_END_OFFSET: 
                    mm_start_offset = reg_if.mask_write_bytes(mm_end_offset);
                endcase
            end
        end     
    end
endmodule



module piradip_axis_sample_buffer_out ( 
        axi4mm_lite axilite,
        axi4mm aximm,
        axi4s stream_out,
        input trigger 
    );

    localparam AXIMM_DATA_WIDTH = $bits(aximm.rdata);
    localparam AXIMM_ADDR_WIDTH = $bits(aximm.araddr);
    
    localparam MEMORY_BIT_WIDTH = AXIMM_ADDR_WIDTH + 3;

    localparam STREAM_DATA_WIDTH = $bits(stream_out.tdata);
    localparam STREAM_ADDR_WIDTH = MEMORY_BIT_WIDTH - $clog2(STREAM_DATA_WIDTH); 

    localparam READ_LATENCY_A=1;
    localparam READ_LATENCY_B=1;

    logic stream_update;
    logic stream_stopped;
    logic stream_active;
    logic stream_one_shot;
    logic [STREAM_ADDR_WIDTH-1:0] stream_start_offset;
    logic [STREAM_ADDR_WIDTH-1:0] stream_end_offset;

    logic enable_stream;

    piradip_ram_if #(.DATA_WIDTH(AXIMM_DATA_WIDTH), .ADDR_WIDTH(MEMORY_BIT_WIDTH-$clog2(AXIMM_DATA_WIDTH))) mem_mm(.clk_in(aximm.aclk), .rst_in(~aximm.aresetn));
    piradip_ram_if #(.DATA_WIDTH(STREAM_DATA_WIDTH), .ADDR_WIDTH(STREAM_ADDR_WIDTH)) mem_stream(.clk_in(stream_out.aclk), .rst_in(~stream_out.aresetn));

    piradip_axis_sample_buffer_csr #(
        .STREAM_OFFSET_WIDTH(STREAM_ADDR_WIDTH)
    ) csr (
        .aximm(axilite),
        .stream_clk(stream_out.aclk),
        .*
    );
    
    
    piradip_tdp_ram ram(.a(mem_mm.RAM_PORT), .b(mem_stream.RAM_PORT));
    
    assign mem_mm.en = 1'b1;
    assign mem_stream.en = 1'b1;
    
    piradip_axi4_ram_adapter #(
        .DATA_WIDTH(AXIMM_DATA_WIDTH),
        .ADDR_WIDTH(AXIMM_ADDR_WIDTH),
        .WE_WIDTH(1), 
        .READ_LATENCY(READ_LATENCY_A)
    ) ram_adapter(
        .aximm(aximm),
        .mem(mem_mm.CLIENT)  
    );
    
    assign mem_stream.we = 0;
    assign mem_stream.wdata = 0;

    axi4s #(.WIDTH(STREAM_DATA_WIDTH)) gearbox_in(.clk(stream_out.aclk), .resetn(stream_out.aresetn));


    piradip_axis_gearbox #(
            .DEPTH(16),
            .PROG_FULL_THRESH(5)
        ) gearbox (
            .in(gearbox_in.SUBORDINATE),
            .out(stream_out)
    );

    piradip_latency_synchronizer #(
        .OUT_OF_BAND_WIDTH(0),
        .IN_BAND_WIDTH(STREAM_DATA_WIDTH),
        .DATA_LATENCY(READ_LATENCY_B)
        ) stream_sync (
            .in_valid(enable_stream),
            .in_band(mem_stream.rdata),
            .out_valid(gearbox_in.tvalid),
            .out_data(gearbox_in.tdata)
        );

    always @(posedge stream_out.aclk)
    begin
        if (~stream_out.aresetn) begin
            enable_stream <= 1'b0;
            stream_stopped <= 1'b0;
        end else begin
            stream_stopped = 1'b0;
            
            if (stream_update) begin
                enable_stream <= stream_active;
            end else if ((mem_stream.addr >= stream_end_offset) && stream_one_shot) begin
                enable_stream <= 1'b0;
                stream_stopped = 1'b1;
            end else begin
                enable_stream <= enable_stream;
            end
        end
    end
    
    always @(posedge stream_out.aclk)
    begin
        if (~stream_out.aresetn) begin
            mem_stream.addr <= 0;
        end else begin
            if (stream_update & stream_active) begin
                mem_stream.addr <= stream_start_offset;
            end else if (enable_stream & gearbox_in.tready) begin
                mem_stream.addr <= (mem_stream.addr >= stream_end_offset) ? stream_start_offset : mem_stream.addr+1;
            end
        end
    end
    
    
endmodule
