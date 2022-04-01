`timescale 1ns / 1ps

package piradip_tb_aximm_util;
endpackage

import piradip_axi4::*;

module piradip_tb_axilite_manager #(
        name="AXI",
        DEBUG=0
    ) (
        axi4mm_lite.MANAGER aximm
    );
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
        axi_resp_t resp;
                
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

    semaphore read_sem;
    semaphore write_sem;

    aximm_op awaddr_queue[$];    
    aximm_op wdata_queue[$];    
    aximm_op bresp_queue[$];    

    aximm_op araddr_queue[$];
    aximm_op rdata_queue[$];
    
    /* Issued, but not completed, reads and writes */
    aximm_op issued_write_queue[$];
    aximm_op issued_read_queue[$];
    
    localparam AWPROT=0;

    task awaddr_task;
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            
            write_sem.get();
            
            if (awaddr_queue.size() != 0) begin
                op = awaddr_queue[0];
                
                if (aximm.awready & aximm.awvalid) begin
                    awaddr_queue.pop_front();
                    op.addr_ack = 1'b1;
                    op = awaddr_queue[0];
                end
    
                if (op != null) begin
                    aximm.awvalid <= 1'b1;
                    aximm.awaddr <= op.addr;
                    aximm.awprot <= AWPROT;
                end else begin
                    aximm.awvalid <= 1'b0;
                    aximm.awaddr <= 0;
                    aximm.awprot <= AWPROT;
                end
            end else begin
                aximm.awvalid <= 1'b0;
                aximm.awaddr <= 0;
                aximm.awprot <= AWPROT;
            end
            write_sem.put();   
        end
    endtask

    task wdata_task;
        integer WSTRB={{aximm.STRB_WIDTH}{1'b1}};

        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            
            write_sem.get();
            
            if (wdata_queue.size() != 0) begin
                op = wdata_queue[0];
                
                if (aximm.awready & aximm.awvalid) begin
                    wdata_queue.pop_front();
                    op.data_ack = 1'b1;
                    op = wdata_queue[0];
                end
    
                if (op != null) begin
                    aximm.wvalid <= 1'b1;
                    aximm.wdata <= op.data;
                    aximm.wstrb <= WSTRB;
                end else begin
                    aximm.wvalid <= 1'b0;
                    aximm.wdata <= 0;
                    aximm.wstrb <= 0;
                end
            end else begin
                aximm.wvalid <= 1'b0;
                aximm.wdata <= 0;
                aximm.wstrb <= 0;
            end
            write_sem.put();   
        end
    endtask

    task bready_task;
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            aximm.bready <= 1;
            
            while (bresp_queue.size() > 0 && bresp_queue[0].opcode == NOOP) begin
                op = bresp_queue.pop_front();
                ->op.e;            
            end
            
            if (aximm.bready & aximm.bvalid) begin
                assert(bresp_queue.size() > 0);
                
                op = bresp_queue.pop_front();
                
                assert(op.addr_ack & op.data_ack);
                
                op.resp = aximm.bresp;
                ->op.e;
            end
        end            
    endtask  

    task araddr_task;
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            
            read_sem.get();
            
            if (araddr_queue.size() != 0) begin
                op = araddr_queue[0];
                
                if (aximm.arready & aximm.arvalid) begin
                    araddr_queue.pop_front();
                    op.addr_ack = 1'b1;
                    op = araddr_queue[0];
                end
    
                if (op != null) begin
                    aximm.arvalid <= 1'b1;
                    aximm.araddr <= op.addr;
                    aximm.arprot <= AWPROT;
                end else begin
                    aximm.arvalid <= 1'b0;
                    aximm.araddr <= 0;
                    aximm.arprot <= AWPROT;
                end
            end else begin
                aximm.arvalid <= 1'b0;
                aximm.araddr <= 0;
                aximm.arprot <= AWPROT;
            end
            
            read_sem.put();   
        end
    endtask
    
    task rready_task;
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            
            aximm.rready <= 1'b1;
    
            read_sem.get();
    
            while (rdata_queue.size() > 0 && rdata_queue[0].opcode == NOOP) begin
                op = rdata_queue.pop_front();
                
                ->op.e;
            end
        
            if (aximm.rready & aximm.rvalid) begin
                assert(rdata_queue.size() > 0);
                
                op = rdata_queue.pop_front();
    
                op.data = aximm.rdata;
                op.resp = aximm.rresp;
                
                ->op.e;       
            end
    
            read_sem.put();   
        end
    endtask    

    task automatic issue_read(input aximm_op op);
        read_sem.get();
    
        if (op.opcode != NOOP) begin    
            araddr_queue.push_back(op);
        end

        rdata_queue.push_back(op);    
        
        read_sem.put();   
    endtask


    task automatic issue_write(input aximm_op op);
        write_sem.get();
        
        if (op.opcode != NOOP) begin    
            awaddr_queue.push_back(op);
            wdata_queue.push_back(op);    
        end
        
        bresp_queue.push_back(op);
        
        write_sem.put();   
    endtask

    mailbox #(aximm_op) op_mbx = new();

    task automatic dispatcher();
        forever
        begin
            automatic aximm_op op;
            automatic aximm_op barrier_op;
            
            op_mbx.get(op);
             
            if (~aximm.aresetn) begin
                -> op.e;
            end else if (op.opcode == READ) begin
                if (op.barrier) begin
                    automatic aximm_op barrier_op = new(NOOP, 1);
                    
                    issue_read(op);
                    issue_write(barrier_op);
                    
                    wait(op.e.triggered && barrier_op.e.triggered);
                end else begin
                    issue_read(op);
                end
            end else if (op.opcode == WRITE) begin
                 if (op.barrier) begin
                    automatic aximm_op barrier_op = new(NOOP, 1);
                    
                    issue_write(op);
                    issue_read(barrier_op);
                    
                    wait(op.e.triggered && barrier_op.e.triggered);
                end else begin
                    issue_write(op);
                end
            end else if (op.opcode == NOOP) begin
                  if (op.barrier) begin
                    automatic aximm_op read_barrier = new(NOOP, 1);
                    automatic aximm_op write_barrier = new(NOOP, 1);
                    
                    issue_write(write_barrier);
                    issue_read(read_barrier);
                    
                    wait(write_barrier.e.triggered && read_barrier.e.triggered);
                    
                    -> op.e;
                end else begin
                    -> op.e;
                end           
            end
        end
    endtask;

    task automatic read(input addr_t addr, ref data_t data);
        aximm_op op = new(READ, 0, addr);
        
        op_mbx.put(op);
        
        wait(op.e.triggered);
        
        data = op.data;
        assert(op.resp == AXI_RESP_OKAY);
        if (DEBUG) $display("%s: Read %x complete: %x", name, addr, data);
    endtask

    task automatic read_resp(input addr_t addr, ref data_t data, ref axi_resp_t resp);
        aximm_op op = new(READ, 0, addr);
        
        op_mbx.put(op);
        
        wait(op.e.triggered);
        
        data = op.data;
        resp = op.resp;
        if (DEBUG) $display("%s: Read %x complete: %x", name, addr, data);
    endtask

    task automatic write(input addr_t addr, input data_t data);
        aximm_op op = new(WRITE, 0, addr, data);
        
        op_mbx.put(op);
        
        wait(op.e.triggered);
        
        data = op.data;
        assert(op.resp == AXI_RESP_OKAY);
        if (DEBUG) $display("%s: Write %x complete: %x", name, addr, data);
    endtask
 
     task automatic write_resp(input addr_t addr, input data_t data, ref axi_resp_t resp);
        aximm_op op = new(WRITE, 0, addr, data);
        
        op_mbx.put(op);
        
        wait(op.e.triggered);
        
        resp = op.resp;
        if (DEBUG) $display("%s: Write %x complete: %x", name, addr, data);
    endtask

    initial
    begin
        write_sem = new(1);
        read_sem = new(1);
        fork
            dispatcher;
            awaddr_task;
            wdata_task;
            bready_task;
            araddr_task;
            rready_task;
        join_none
    end

endmodule
