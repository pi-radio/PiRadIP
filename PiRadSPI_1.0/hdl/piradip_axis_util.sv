`timescale 1ns / 1ps


module piradip_util_axis_slave #(
    parameter WIDTH=32
) (
    input wire clk,
    input wire aresetn,
    input string name,
    axis_simple slavein
);
    wire [WIDTH-1:0] tdata;
    wire tvalid;
    reg tready;
    wire tlast;
    
    initial 
    begin
        slavein.tready <= 1;
        
        forever begin
            @(posedge clk) if (slavein.tvalid) begin
                $display("%s: Recieved: %x%s", name, slavein.tdata, slavein.tlast ? " LAST" : "");
            end
        end;
    end
        
endmodule
    
module piradip_util_axis_master #(
    parameter WIDTH=32
) (
    input wire clk,
    input wire aresetn,
    input string name,
    axis_simple masterout
);
    typedef enum {
        WRITE,
        SYNC
    } opcode_t;
    
    class op_t;
        opcode_t code;
        reg [WIDTH-1:0] data;
        event e;
        
        function new (input opcode_t code, input logic [WIDTH-1:0] data);
            this.code = code;
            this.data = data;
        endfunction           
    endclass
           
    op_t op_q[$];
    
    function automatic send_one(input logic [WIDTH-1:0] data);
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
        masterout.tdata = 0;
        masterout.tvalid = 0;
        masterout.tlast = 0;
        
        forever
        begin
            wait(op_q.size() != 0);

            cur_op = op_q.pop_front();
            $display("%s: (%t) Master operation %d %x", name, $time, cur_op.code.name, cur_op.data);
            
            case (cur_op.code)
                WRITE: begin
                    masterout.tdata = cur_op.data;
                    masterout.tvalid = 1;
                    wait(masterout.tvalid & masterout.tready);
                    @(posedge clk) masterout.tvalid = 0;
                    $display("%s: (%t) Master write complete (%x)", name, $time, cur_op.data);   
                end

                SYNC: -> cur_op.e;
            endcase
        end        
    end  
endmodule
