`timescale 1ns / 1ps


module piradip_util_axis_slave #(
    parameter WIDTH=32
) (
    input wire clk,
    input wire aresetn,
    input string name
);
    wire [WIDTH-1:0] tdata;
    wire tvalid;
    reg tready;
    wire tlast;
    
    initial 
    begin
        tready <= 1;
        
        forever begin
            @(posedge clk) if (tvalid) begin
                $display("%s: Recieved: %x", name, tdata);
            end
        end;
    end
        
endmodule
    
module piradip_util_axis_master #(
    parameter WIDTH=32
) (
    input wire clk,
    input wire aresetn,
    input string name
);
    reg [WIDTH-1:0] tdata;
    reg tvalid;
    wire tready;
    reg tlast;
        
    typedef enum {
        WRITE,
        SYNC
    } opcode_t;
    
    class op_t;
        opcode_t code;
        logic [WIDTH-1:0] data;
        event e;
        
        function new (input opcode_t code, input logic [WIDTH-1:0] data);
            this.code = code;
            this.data = data;
        endfunction           
    endclass
           
    op_t op_q[$];
    
    task send_one(input logic [WIDTH-1:0] data);
        automatic op_t op = new(WRITE, data);
        
        op_q.push_back(op);   
    endtask
    
    initial
    begin
        op_t op;
        tdata <= 0;
        tvalid <= 0;
        tlast <= 0;
        
        fork
            forever @(posedge clk) begin
                while (op_q.size() > 0) 
                begin
                    op = op_q.pop_front();
                    $display("%s: Master operation %d", name, op.code);
                    
                    case (op.code)
                        WRITE: begin
                            tdata <= op.data;
                            tvalid <= 1;
                            do @(posedge clk); while(~tready);
                            $display("%s: Master write complete (%x)", name, op.data);   
                        end
                        
                        SYNC: -> op.e;
                    endcase;
                end

                tvalid <= 0;
             end
        join_none;
    end  
endmodule
