`timescale 1ns / 1ps

`include "piradip_axi4.svh"

import piradip_axi4::*;

module piradip_util_axis_subordinate #(
    parameter WIDTH=32
) (
    input string name,
    axis_simple sub_in
);
    always_comb sub_in.tready <= sub_in.aresetn;

    always @(posedge sub_in.aclk) begin
        if (sub_in.tvalid) begin
            $display("%s: Recieved: %x%s", name, sub_in.tdata, sub_in.tlast ? " LAST" : "");
        end
    end;
    
endmodule

module piradip_util_axis_inc_manager (
    input string name,
    axis_simple manager_out
);
    logic [manager_out.WIDTH-1:0] counter;
    
    always_comb manager_out.tvalid <= 1'b1;
    always_comb manager_out.tdata <= counter;
    always_comb manager_out.tlast <= 1'b0;
    
    always @(posedge manager_out.aclk)
    begin
        if (~manager_out.aresetn) begin
            counter <= 0;
        end else if (manager_out.tvalid & manager_out.tready) begin
            counter <= counter + 1;
        end
    end
    
endmodule
    
module piradip_util_axis_manager (
    input string name,
    axis_simple manager_out
);
    typedef logic [manager_out.WIDTH-1:0] data_word_t;
    
    typedef enum {
        WRITE,
        SYNC
    } opcode_t;
    
    class op_t;
        opcode_t code;
        data_word_t data;
        event e;
        
        function new (input opcode_t code, input data_word_t data);
            this.code = code;
            this.data = data;
        endfunction           
    endclass
           
    op_t op_q[$];
    
    function automatic send_one(input data_word_t data);
        automatic op_t op = new(WRITE, data);
        
        op_q.push_back(op);   
    endfunction
   
    task automatic sync();
        automatic op_t op = new(SYNC, 0);
        
        op_q.push_back(op);
        
        wait(op.e.triggered);
        $display("%s: SYNC complete", name);
    endtask
    
    op_t cur_op;
    
    reg wait_flag;
        
    initial
    begin
        manager_out.tdata = 0;
        manager_out.tvalid = 0;
        manager_out.tlast = 0;
        
        forever
        begin
            wait(op_q.size() != 0);

            cur_op = op_q.pop_front();
            $display("%s: (%t) manager operation %d %x", name, $time, cur_op.code.name, cur_op.data);
            
            case (cur_op.code)
                WRITE: begin
                    manager_out.tdata = cur_op.data;
                    manager_out.tvalid = 1;
                    wait(manager_out.tvalid & manager_out.tready);
                    @(posedge manager_out.clk) manager_out.tvalid = 0;
                    $display("%s: (%t) manager write complete (%x)", name, $time, cur_op.data);   
                end

                SYNC: -> cur_op.e;
            endcase
        end        
    end  
endmodule
