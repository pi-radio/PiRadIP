`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 10/26/2021 12:50:22 PM
// Design Name: 
// Module Name: piradip_tb_aximm_util
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

interface aximm_lite #(
    parameter integer ADDR_WIDTH=8,
    parameter integer DATA_WIDTH=32
)(input logic aclk, input logic aresetn);
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
    logic [DATA_WIDTH-1 : 0] araddr;
    logic [2 : 0] arprot;
    logic arvalid;
    logic arready;
    logic [DATA_WIDTH-1 : 0] rdata;
    logic [1 : 0] rresp;
    logic rvalid;
    logic rready;
    

    
    modport MANAGER(input awready, wready, bresp, bvalid, rdata, rresp, rvalid,
                    output awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready);

    modport SUBORDINATE(output awready, wready, bresp, bvalid, rdata, rresp, rvalid,
                        input awaddr, awprot, awvalid, wdata, wstrb,
                          wvalid, bready, araddr, arprot, arvalid, rready);

endinterface

module piradip_tb_axilite_master #(
    ) (
        input string name,
        aximm_lite aximm
    );
    
    localparam DATA_WIDTH=aximm.DATA_WIDTH;
    localparam ADDR_WIDTH=aximm.ADDR_WIDTH;

    typedef logic [aximm.ADDR_WIDTH-1:0] addr_t;
    typedef logic [aximm.DATA_WIDTH-1:0] data_t;

    typedef enum {
        NOOP = 0,
        READ = 1,
        WRITE = 2
    } opcode_t;

    class aximm_op;
        opcode_t opcode;
        logic barrier;
        addr_t addr;
        data_t data;
        logic addr_ack;
        logic data_ack;
        event e;
        
        function new(input opcode_t opcode, input logic barrier, input addr_t addr = 0, input data_t data = 0);
            this.opcode = opcode;
            this.barrier = barrier;
            this.addr = addr;
            this.data = data;
            this.addr_ack = 0;
            this.data_ack = 0;
        endfunction
    endclass

    aximm_op queue[$];
    aximm_op read_queue[$];
    aximm_op wire_queue[$];
    
    
    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin

            aximm.bready <= 0; 
            aximm.araddr <= 0;
            aximm.arprot <= 0;
            aximm.arvalid <= 0;
            aximm.rready <= 0;
            
            
        end else begin
        end
    end

    localparam AWPROT=0;
    localparam WSTRB={{aximm.STRB_WIDTH}{1'b1}};

    aximm write_op, read_op;

    task next_write();
        do begin
            write_op = write_queue.pop_front();
            
            if (write_op.opcode == NOOP) begin
                -> write_op.e;
                write_op = null;
            end else if (write_op.opcode == WRITE) begin
                aximm.awprot = AWPROT;
                aximm.awaddr = write_op.data;
                aximm.awvalid = 1;
                
                aximm.wdata = write_op.data;
                aximm.wstrb = WSTRB;
                aximm.wvalid = 1;
            end else begin
                $error("%s: Write queue has invalid opcode %s", name, write_op.opcode.name);
                write_op = null;
            end
        end while(write_op == null && write_queue.size());        
    endtask;

    always @(posedge aximm.aclk)
    begin
        if (~aximm.aresetn) begin
            aximm.awaddr <= 0;
            aximm.awprot <= 0;
            aximm.awvalid <= 0;
            aximm.wdata <= 0;
            aximm.wstrb <= 0;
            aximm.wvalid <= 0;
            write_op = null;
        end else if(write_op != null) begin
            write_op.addr_ack = write_op.addr_ack | (aximm.awvalid & aximm.awready);
            write_op.data_ack = write_op.data_ack | (aximm.wvalid & aximm.wready);
            
            aximm.awvalid = write_op.awvalid & ~aximm.awready;
            aximm.wvalid = write_op.wvalid & ~aximm.wready;
            
            if (write_op.addr_ack & write_op.data_ack) begin
                -> write_op.e;
                if (queue.size() != 0) begin
                    write_op = queue.pop_front();
                    next_write();
                end else begin
                    write_op = null;
                end
            end
        end else if(queue.size() != 0) begin
            next_write();
        end
    end
        
    task automatic dispatcher();
        forever
        begin          
            aximm_op op = queue.pop_front();
            
            if (~aximm.aresetn) begin
                -> op.e;
            end else if (op.copcode == READ) begin
                if (op.barrier) begin
                    automatic aximm_op barrier_op = new(NOOP, 1);
                    
                    read_queue.push_back(op);
                    write_queue.push_back(barrier_op);
                    
                    wait(op.e.triggered && barrier_op.e.triggered);
                end else begin
                    read_queue.push_back(op);
                end
            end else if (op.opcode == WRITE) begin
                 if (op.barrier) begin
                    automatic aximm_op barrier_op = new(NOOP, 1);
                    
                    write_queue.push_back(op);
                    read_queue.push_back(barrier_op);
                    
                    wait(op.e.triggered && barrier_op.e.triggered);
                end else begin
                    write_queue.push_back(op);
                end
            end else if (op.opcode == NOOP) begin
                  if (op.barrier) begin
                    automatic aximm_op read_barrier = new(NOOP, 1);
                    automatic aximm_op write_barrier = new(NOOP, 1);
                    
                    write_queue.push_back(write_barrier);
                    read_queue.push_back(read_barrier);
                    
                    wait(write_barrier.e.triggered && read_barrier.e.triggered);
                    
                    -> op.e;
                end else begin
                    -> op.e;
                end           
            end
        end
    endtask;

    initial
    begin
        fork
            dispatcher();
        join;
    end

endmodule
