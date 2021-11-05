`include "piradip_aximm.svh"

import piradip_axi4::*;

interface axi4mm_lite #(
    parameter integer ADDR_WIDTH=8,
    parameter integer DATA_WIDTH=32
)(
    input logic aclk, 
    input logic aresetn
);
    localparam STRB_WIDTH=(DATA_WIDTH/8);
    
    logic [ADDR_WIDTH-1 : 0] awaddr;
    logic [2 : 0] awprot;
    logic awvalid;
    logic awready;
    logic [DATA_WIDTH-1 : 0] wdata;
    logic [STRB_WIDTH-1 : 0] wstrb;
    logic wvalid;
    logic wready;
    logic [1 : 0] bresp;
    logic bvalid;
    logic bready;
    logic [ADDR_WIDTH-1 : 0] araddr;
    logic [2 : 0] arprot;
    logic arvalid;
    logic arready;
    logic [DATA_WIDTH-1 : 0] rdata;
    logic [1 : 0] rresp;
    logic rvalid;
    logic rready;
    
    modport MANAGER(input aclk, aresetn, awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid,
                    output awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready);

    modport SUBORDINATE(output awready, wready, bresp, bvalid, arready, rdata, rresp, rvalid,
                        input aclk, aresetn, awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready);

endinterface

interface piradip_register_if #(
        parameter integer DATA_WIDTH = 32,
        parameter integer REGISTER_ADDR_BITS = 8
    )(
        input aclk,
        input aresetn
    );

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;

    logic wren;
    regno_t wreg_no;
    logic [DATA_WIDTH-1:0] wreg_data;
    logic rden;
    regno_t rreg_no;
    logic [DATA_WIDTH-1:0] rreg_data;       

    modport CLIENT(output wren, wreg_no, wreg_data, rden, rreg_no, input rreg_data);
    modport SERVER(input wren, wreg_no, wreg_data, rden, rreg_no, output rreg_data);
    
    function automatic logic is_reg_read(input regno_t regno);
        return rden && rreg_no == regno;
    endfunction;

    function automatic logic is_reg_write(input regno_t regno);
        if (wren) $display("WRITE EN: %x %x", wreg_no, regno);
        return wren && wreg_no == regno;
    endfunction;
   
endinterface

module piradip_axi4mmlite_subordinate #(
        localparam integer DATA_WIDTH = aximm.DATA_WIDTH,
        localparam integer ADDR_LSB = (aximm.DATA_WIDTH/32) + 1,
        localparam integer REGISTER_ADDR_BITS = aximm.ADDR_WIDTH - ADDR_LSB
    )(
        axi4mm_lite aximm,
        piradip_register_if reg_if
    );
      
    logic aw_en;
    logic [aximm.ADDR_WIDTH-1:0] awaddr_r;
    logic [aximm.ADDR_WIDTH-1:0] araddr_r;
    
    assign reg_if.rden = aximm.arready & aximm.arvalid & ~aximm.rvalid;

    typedef logic [REGISTER_ADDR_BITS-1:0] regno_t;
    
    function automatic logic [aximm.DATA_WIDTH-1:0] mask_write_bytes(input logic [aximm.DATA_WIDTH-1:0] r);
        integer	 i;
        logic [aximm.DATA_WIDTH-1:0] retval;;
        for ( i = 0; i < aximm.STRB_WIDTH; i = i+1 ) begin
            retval[(i*8) +: 8] = aximm.wstrb[i] ? aximm.wdata[(i*8) +: 8] : r[(i*8) +: 8];
        end
        return retval;     
    endfunction

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
            reg_if.wreg_data <= aximm.wdata;
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

module register_to_stream #(
    parameter DATA_WIDTH = 32,
    parameter REGISTER_NO = 0
) (
    output logic do_issue,
    output logic failed_issue,
    output logic [DATA_WIDTH-1:0] read_data,
    piradip_register_if reg_if,
    axis_simple stream
);
    assign do_issue =  reg_if.is_reg_write(REGISTER_NO) && ~(stream.tvalid & ~stream.tready);
     
    assign read_data = { failed_issue, stream.tready };

    always @(posedge aximm.aclk)
    begin   
        if (~reg_if.aresetn) begin
            stream.tvalid <= 1'b0;
            failed_issue <= 1'b0;
        end else if (reg_if.is_reg_write(REGISTER_NO)) begin
            if (do_issue) begin
                stream.tvalid <= 1'b1;
            end else begin
                failed_issue <= 1;
            end
        end else begin
            if (reg_if.wren) $display("VALS: %x, %x, %x", REGISTER_NO, reg_if.wreg_no, reg_if.wren);
            
            failed_issue <= reg_if.is_reg_read(REGISTER_NO) ? 0 : failed_issue;
            axis_cmd.tvalid <= axis_cmd.tvalid & ~axis_cmd.tready;
        end
    end    
    
endmodule

