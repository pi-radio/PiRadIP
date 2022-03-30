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
    
    input logic stream_clk,
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
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            mm_active <= 1'b0;
            mm_one_shot <= 1'b0;
            mm_start_offset <= 0;
            mm_end_offset <= {STREAM_OFFSET_WIDTH{1'b1}};
        end else if(reg_if.wren) begin
            mm_update <= 1'b0;
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
endmodule



module piradip_axis_sample_buffer_out ( 
        axi4mm_lite axilite,
        axi4mm aximm,
        axi4s stream_out 
    );

    localparam MEMORY_DATA_WIDTH=$bits(aximm.rdata);
    localparam MEMORY_ADDR_WIDTH=$bits(aximm.araddr);

    localparam MEMORY_BITS = (MEMORY_DATA_WIDTH << MEMORY_ADDR_WIDTH);

    localparam STREAM_DATA_WIDTH=$bits(stream_out.tdata);
    localparam STREAM_ADDR_WIDTH = $clog2(MEMORY_BITS) - $clog2(STREAM_DATA_WIDTH); 

    localparam READ_LATENCY_A=1;
    localparam READ_LATENCY_B=1;

    logic stream_update;
    logic stream_active;
    logic stream_one_shot;
    logic [STREAM_ADDR_WIDTH-1:0] stream_start_offset;
    logic [STREAM_ADDR_WIDTH-1:0] stream_end_offset;

    logic enable_stream, stream_disabled;

    piradip_axis_sample_buffer_csr #(
        .STREAM_OFFSET_WIDTH(STREAM_ADDR_WIDTH)
    ) csr (
        .aximm(axilite),
        .stream_clk(stream_out.aclk),
        .*
    );
    
    piradip_ram_if #(.DATA_WIDTH(MEMORY_DATA_WIDTH), .ADDR_WIDTH(MEMORY_ADDR_WIDTH)) mem_mm(.clk_in(aximm.aclk), .rst_in(~aximm.aresetn));
    piradip_ram_if #(.DATA_WIDTH(STREAM_DATA_WIDTH), .ADDR_WIDTH(STREAM_ADDR_WIDTH)) mem_stream(.clk_in(stream_out.aclk), .rst_in(~stream_out.aresetn));
    
    piradip_tdp_ram ram(.a(mem_mm.RAM_PORT), .b(mem_stream.RAM_PORT));
    
    assign mem_mm.en = 1'b1;
    assign mem_stream.en = 1'b1;
    
/*
    logic [MEMORY_LOG2_WORDS-1:0] addr_a;
    logic [MEMORY_DATA_WIDTH-1:0] rdata_a;
    logic [MEMORY_DATA_WIDTH-1:0] wdata_a;
    logic wen_a;
    
    logic [STREAM_LOG2_WORDS-1:0] addr_b;
    logic [STREAM_DATA_WIDTH-1:0] rdata_b;
    logic [STREAM_DATA_WIDTH-1:0] wdata_b;
    logic wen_b;


    
        
    xpm_memory_tdpram #(
        .ADDR_WIDTH_A(MEMORY_LOG2_WORDS),
        .BYTE_WRITE_WIDTH_A(32),
        .READ_DATA_WIDTH_A(32),
        .READ_LATENCY_A(READ_LATENCY_A),
        .READ_RESET_VALUE_A(0),
        .RST_MODE_A("SYNC"),
        .WRITE_DATA_WIDTH_A(MEMORY_DATA_WIDTH),
        .WRITE_MODE_A(" write_first"),

        .ADDR_WIDTH_B(STREAM_LOG2_WORDS),
        .BYTE_WRITE_WIDTH_B(STREAM_DATA_WIDTH),
        .READ_DATA_WIDTH_B(STREAM_DATA_WIDTH),
        .READ_LATENCY_B(READ_LATENCY_B),
        .READ_RESET_VALUE_B(0),
        .RST_MODE_B("SYNC"),
        .WRITE_DATA_WIDTH_B(STREAM_DATA_WIDTH),
        .WRITE_MODE_B("write_first"),

        
        .CASCADE_HEIGHT(0),
        .CLOCKING_MODE("independent_clock"),
        .ECC_MODE("no_ecc"),
        .MEMORY_INIT_FILE("none"),
        .MEMORY_INIT_PARAM("0"),
        .MEMORY_OPTIMIZATION("true"),
        .MEMORY_PRIMITIVE("auto"),
        .MEMORY_SIZE(MEMORY_DATA_WIDTH * (1 << MEMORY_LOG2_WORDS)),
        .MESSAGE_CONTROL(0),
        .SIM_ASSERT_CHK(1),
        .WAKEUP_TIME("disable_sleep")        
    ) sample_buffer_ram (
        .sleep(1'b0),
        
        .clka(aximm.aclk),
        .rsta(~aximm.aresetn),
        .ena(1'b1),
        .wea(wen_a),
        .addra(addr_a),
        .dina(wdata_a),
        .douta(rdata_a),
        .regcea(1'b1),
        
        .clkb(stream_out.aclk),
        .rstb(~stream_out.aresetn),
        .enb(1'b1),
        .web(wen_b),
        .addrb(addr_b),
        .dinb(wdata_b),
        .doutb(rdata_b),
        .regceb(1'b1)
    );
*/
    piradip_axi4_ram_adapter #(
        .DATA_WIDTH(MEMORY_DATA_WIDTH),
        .ADDR_WIDTH(MEMORY_ADDR_WIDTH),
        .WE_WIDTH(1), 
        .READ_LATENCY(READ_LATENCY_A)
    ) ram_adapter(
        .aximm(aximm),
        .mem(mem_mm.CLIENT)  
    );

    assign mem_stream.we = 0;
    assign mem_stream.wdata = 0;
    
    assign stream_out.tdata = 0;


    
    always @(posedge stream_out.aclk)
    begin
        if (~stream_out.aresetn) begin
        end else begin
        end
    end
    

    
endmodule
