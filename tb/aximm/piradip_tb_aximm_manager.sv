`timescale 1ns / 1ps

import piradip_axi4::*;

module piradip_tb_aximm_manager #(
        name="AXI",
        DEBUG=0
    ) (
        axi4mm.MANAGER aximm
    );
    
    import piradip_axi4::*;
    
    typedef logic [aximm.ADDR_WIDTH-1:0] addr_t;
    typedef logic [aximm.DATA_WIDTH-1:0] data_t;

    localparam WORD_BURST_SIZE = (aximm.DATA_WIDTH == 32) ? AXI_SIZE_4 :
        (aximm.DATA_WIDTH == 62) ? AXI_SIZE_8 : AXI_SIZE_1;

    typedef enum {
        NOOP = 0,
        READ = 1,
        WRITE = 2
    } opcode_t;

    class aximm_op;
        opcode_t opcode;
        logic complete;
        logic barrier;
        addr_t addr;
        data_t data;
        logic addr_sent;
        logic data_sent;
        axi_resp_t resp;
                
        event e;
        
        function new(input opcode_t opcode, input logic barrier, input addr_t addr = 0, input data_t data = 0);
            this.opcode = opcode;
            this.barrier = barrier;
            this.addr = addr;
            this.data = data;
            this.complete = 1'b0;
        endfunction
        
        function void set_complete(input axi_resp_t resp);
            this.complete = 1'b1;
            this.resp = resp;
            ->this.e;
        endfunction
    endclass

    semaphore read_sem;
    semaphore write_sem;

    mailbox #(aximm_op) awaddr_mbx = new();
    mailbox #(aximm_op) wdata_mbx = new();
    mailbox #(aximm_op) bresp_mbx = new();

    mailbox #(aximm_op) araddr_mbx = new();
    mailbox #(aximm_op) rdata_mbx = new();
    
    /* Issued, but not completed, reads and writes */
    aximm_op issued_write_queue[$];
    aximm_op issued_read_queue[$];
    
    localparam AWPROT=0;

    task awaddr_task;
        aximm.awvalid <= 1'b0;
        aximm.awaddr <= 0;
        aximm.awprot <= 0;
        aximm.awlen <= 0;
        aximm.awid <= 0;
        aximm.awburst <= 0;
        aximm.awsize <= 0;
        aximm.awlock <= 0;
        aximm.awcache <= 0;
        aximm.awqos <= 0;
        aximm.awregion <= 0;
        aximm.awuser <= 0;
        
        forever begin
            automatic aximm_op op;

            while (awaddr_mbx.num() == 0) @(posedge aximm.aclk);            

            awaddr_mbx.get(op);
            
            if (op.opcode == WRITE) begin
                aximm.awvalid <= 1'b1;
                aximm.awaddr <= op.addr;
                aximm.awprot <= AWPROT;
                aximm.awlen <= 1;
                aximm.awid <= 0;
                aximm.awburst <= AXI_BURST_INCR;
                aximm.awsize <= WORD_BURST_SIZE;
                aximm.awlock <= AXI_LOCK_NORMAL;
                aximm.awcache <= AXI_CACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE;
                aximm.awqos <= 0;
                aximm.awregion <= 0;
                aximm.awuser <= 0;
    
                #1step while(~aximm.awready) @(posedge aximm.aclk);
                wdata_mbx.put(op);
                bresp_mbx.put(op);
                @(posedge aximm.aclk);
                
                aximm.awvalid <= 1'b0;
            end else begin
                bresp_mbx.put(op);
            end
        end     
    endtask

    task wdata_task;
        static integer WSTRB={{aximm.STRB_WIDTH}{1'b1}};

        aximm.wvalid <= 1'b0;
        aximm.wdata <= 0;
        aximm.wstrb <= WSTRB;
        aximm.wlast <= 1'b0;
        
        forever begin
            automatic aximm_op op;

            while (wdata_mbx.num() == 0) @(posedge aximm.aclk);            

            wdata_mbx.get(op);
            aximm.wvalid <= 1'b1;
            aximm.wdata <= op.data;
            aximm.wstrb <= WSTRB;
            
            #1step while (~aximm.wready) @(posedge aximm.aclk);
            @(posedge aximm.aclk);
            
            aximm.wvalid <= 1'b0;
        end
    endtask

    task bready_task;
        automatic aximm_op pending[$];

        aximm.bready <= 1;
        
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
        
            while (bresp_mbx.num()) begin
                bresp_mbx.get(op);
                pending.push_back(op);                    
            end
            
            while (pending.size() > 0 && pending[0].opcode == NOOP) begin
                op = pending.pop_front();
                op.set_complete(AXI_RESP_OKAY);
            end
            
            if (aximm.bready & aximm.bvalid) begin
                assert(pending.size() > 0) else $display("%t: ERROR: No pending writes", $time());
                
                op = pending.pop_front();
                
                op.set_complete(aximm.bresp);                
            end
        end 
    endtask  

    task araddr_task;
        aximm.arvalid <= 1'b0;
        aximm.araddr <= 0;
        aximm.arprot <= 0;
        aximm.arlen <= 0;
        aximm.arid <= 0;
        aximm.arburst <= 0;
        aximm.arsize <= 0;
        aximm.arlock <= 0;
        aximm.arcache <= 0;
        aximm.arqos <= 0;
        aximm.arregion <= 0;
        aximm.aruser <= 0;
        
        forever begin
            automatic aximm_op op;

            while (araddr_mbx.num() == 0) @(posedge aximm.aclk);            

            araddr_mbx.get(op);
            
            if (op.opcode == READ) begin
                aximm.arvalid <= 1'b1;
                aximm.araddr <= op.addr;
                aximm.arprot <= AWPROT;
                aximm.arlen <= 1;
                aximm.arid <= 0;
                aximm.arburst <= AXI_BURST_INCR;
                aximm.arsize <= WORD_BURST_SIZE;
                aximm.arlock <= AXI_LOCK_NORMAL;
                aximm.arcache <= AXI_CACHE_NORMAL_NON_CACHEABLE_NON_BUFFERABLE;
                aximm.arqos <= 0;
                aximm.arregion <= 0;
                aximm.aruser <= 0;
    
                #1step while(~aximm.arready) @(posedge aximm.aclk);
                rdata_mbx.put(op);
                @(posedge aximm.aclk);
                
                aximm.arvalid <= 1'b0;
            end else if (op.opcode == NOOP) begin
                rdata_mbx.put(op);
            end
        end
    endtask
    
    task rready_task;
        automatic aximm_op pending[$];

        aximm.rready <= 1'b1;
        
        forever @(posedge aximm.aclk) begin
            automatic aximm_op op;
            
            while (rdata_mbx.num()) begin
                rdata_mbx.get(op);
                pending.push_back(op);                    
            end
            
            while (pending.size() > 0 && pending[0].opcode == NOOP) begin
                op = pending.pop_front();
                op.set_complete(AXI_RESP_OKAY);                
                ->op.e;            
            end
            
            if (aximm.rready & aximm.rvalid) begin
                assert(pending.size() > 0) begin
                    op = pending.pop_front();
                                    
                    op.data = aximm.rdata;                                
                    op.set_complete(aximm.rresp);                
                end else begin
                    $display("%t: ERROR: No pending reads", $time());
                end
            end
        end     
    endtask    

    task automatic issue_read(input aximm_op op);
        araddr_mbx.put(op);
    endtask


    task automatic issue_write(input aximm_op op);
        awaddr_mbx.put(op);
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
                    
                    wait(op.complete && barrier_op.complete);
                end else begin
                    issue_read(op);
                end
            end else if (op.opcode == WRITE) begin
                 if (op.barrier) begin
                    automatic aximm_op barrier_op = new(NOOP, 1);
                    
                    issue_write(op);
                    issue_read(barrier_op);
                    
                    wait(op.complete && barrier_op.complete);
                end else begin
                    issue_write(op);
                end
            end else if (op.opcode == NOOP) begin
                  if (op.barrier) begin
                    automatic aximm_op read_barrier = new(NOOP, 1);
                    automatic aximm_op write_barrier = new(NOOP, 1);
                    
                    issue_write(write_barrier);
                    issue_read(read_barrier);
                    
                    wait(write_barrier.complete && read_barrier.complete);
                    
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
        assert(op.resp == AXI_RESP_OKAY) else $display("%t: AXI Transaction failed", $time());
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
    
    task automatic write_faf(input addr_t addr, input data_t data);
        aximm_op op = new(WRITE, 0, addr, data);
        
        op_mbx.put(op);
        
        fork
            begin
                wait(op.e.triggered);
                
                data = op.data;
                assert(op.resp == AXI_RESP_OKAY);
                if (DEBUG) $display("%s: Write %x complete: %x", name, addr, data);
            end
        join_none
    endtask
    
    task automatic sync();
        aximm_op op = new(NOOP, 1'b1, 0, 0);
        
        op_mbx.put(op);
        
        wait(op.e.triggered);
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
