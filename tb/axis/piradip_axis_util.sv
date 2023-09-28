`timescale 1ns / 1ps

`include "piradip_axi4.svh"

module piradip_util_axis_subordinate #(
    parameter WIDTH=32
) (
    input string name,
    axis_simple sub_in
);
    logic tvalid, tlast, tready, aresetn;
    logic [WIDTH-1:0] tdata;

    assign aresetn = sub_in.aresetn;
    assign tvalid = sub_in.tvalid;
    assign tlast = sub_in.tvalid;
    assign tdata = sub_in.tdata;
    assign sub_in.tready = tready;

    default clocking SUB_CB @(posedge sub_in.aclk);
        input tvalid, tlast, tdata, aresetn;
        output tready;
    endclocking

    logic [WIDTH-1:0] recv_q[$];

    always @SUB_CB begin
        if (tready & SUB_CB.tvalid) begin
            $display("%s: Recieved: %x%s", name, SUB_CB.tdata, SUB_CB.tlast ? " LAST" : "");
            recv_q.push_back(SUB_CB.tdata);
        end
    end;

    function automatic void ready();
        SUB_CB.tready <= 1'b1;
    endfunction

    function automatic void unready();
        SUB_CB.tready <= 1'b0;
    endfunction

    task automatic recv_one(output logic [WIDTH-1:0] result);
        logic old_tready = tready;

        SUB_CB.tready <= 1;

        wait(recv_q.size() != 0);

        result = recv_q.pop_front();

        SUB_CB.tready <= old_tready;
    endtask

    initial
    begin
        SUB_CB.tready <= 1'b0;
    end
endmodule

module piradip_util_axis_inc_manager#(
    parameter WIDTH=32
) (
    input string name,
    axis_simple.MANAGER manager_out
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

module piradip_util_axis_manager #(
    parameter WIDTH=32
)(
    input string name,
    axis_simple.MANAGER manager_out
);
    logic tvalid, tlast, tready, aresetn;
    logic [WIDTH-1:0] tdata;

    assign manager_out.tvalid = tvalid;
    assign manager_out.tlast = tvalid;
    assign manager_out.tdata = tdata;
    assign tready = manager_out.tready;
    assign aresetn = manager_out.aresetn;

    default clocking MAN_CB @(posedge manager_out.aclk);
        output tvalid, tlast, tdata;
        input tready, aresetn;
    endclocking

    typedef logic [WIDTH-1:0] data_word_t;

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

    function automatic void send_one(input data_word_t data);
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


        @MAN_CB;

        forever
        begin
            MAN_CB.tdata <= 0;
            MAN_CB.tvalid <= 0;
            MAN_CB.tlast <= 0;

            wait(op_q.size() != 0);

            cur_op = op_q.pop_front();

            do begin
                $display("%s: (%t) manager operation %d %x", name, $time, cur_op.code.name, cur_op.data);

                case (cur_op.code)
                    WRITE: begin
                        MAN_CB.tdata <= cur_op.data;
                        MAN_CB.tvalid <= 1;
                        $display("%s: (%t) manager write data out (%x r: %d v: %d)", name, $time, cur_op.data, MAN_CB.tready, tvalid);
                        @(MAN_CB iff tvalid == 1 && MAN_CB.tready == 1);
                        $display("%s: (%t) manager write complete (%x r: %d v: %d)", name, $time, cur_op.data, MAN_CB.tready, tvalid);
                    end

                    SYNC: -> cur_op.e;
              endcase
              cur_op = op_q.pop_front();
            end while(cur_op);
        end
    end
endmodule




module piradip_util_axi4s_subordinate #(
    parameter WIDTH=32
) (
    input string name,
    axi4s.SUBORDINATE sub_in
);
    logic tvalid, tlast, tready, aresetn;
    logic [WIDTH-1:0] tdata;

    assign aresetn = sub_in.aresetn;
    assign tvalid = sub_in.tvalid;
    assign tlast = sub_in.tvalid;
    assign tdata = sub_in.tdata;
    assign sub_in.tready = tready;

    default clocking SUB_CB @(posedge sub_in.aclk);
        input tvalid, tlast, tdata, aresetn;
        output tready;
    endclocking

    logic [WIDTH-1:0] recv_q[$];

    always @SUB_CB begin
        if (tready & SUB_CB.tvalid) begin
            $display("%s: Recieved: %x%s", name, SUB_CB.tdata, SUB_CB.tlast ? " LAST" : "");
            recv_q.push_back(SUB_CB.tdata);
        end
    end;

    function automatic void ready();
        SUB_CB.tready <= 1'b1;
    endfunction

    function automatic void unready();
        SUB_CB.tready <= 1'b0;
    endfunction

    task automatic recv_one(output logic [WIDTH-1:0] result);
        logic old_tready = tready;

        SUB_CB.tready <= 1;

        wait(recv_q.size() != 0);

        result = recv_q.pop_front();

        SUB_CB.tready <= old_tready;
    endtask

    initial
    begin
        SUB_CB.tready <= 1'b0;
    end
endmodule

module piradip_util_axi4s_manager
(
    input string name,
    axi4s.MANAGER manager_out
);
  localparam STREAM_WIDTH = manager_out.data_width();
  
  logic tvalid, tlast, tready, aresetn;
  logic [STREAM_WIDTH-1:0] tdata;

  assign manager_out.tvalid = tvalid;
  assign manager_out.tlast = tlast;
  assign manager_out.tdata = tdata;
  assign tready = manager_out.tready;
  assign aresetn = manager_out.aresetn;
  
  default clocking MAN_CB @(posedge manager_out.aclk);
    output tvalid, tlast, tdata;
    input tready, aresetn;
  endclocking

  typedef logic [STREAM_WIDTH-1:0] data_word_t;
  
  typedef enum {
		WRITE,
		SYNC
		} opcode_t;

  class op_t;
    opcode_t code;
    int tlast;
    data_word_t data;
    event e;
    
    function new (input opcode_t code, input data_word_t data=0, input int tlast=0);
      this.code = code;
      this.data = data;
      this.tlast = tlast;
    endfunction
  endclass

  op_t op_q[$];
  
  function automatic void send_one(input data_word_t data, int tlast=0);
    automatic op_t op = new(WRITE, data, tlast);
    
    op_q.push_back(op);
  endfunction

  task automatic sync();
    automatic op_t op = new(SYNC);
    
    op_q.push_back(op);
    
    wait(op.e.triggered);
    $display("%s: SYNC complete", name);
  endtask
  
  op_t cur_op;
  
  reg wait_flag;
  
  initial
    begin
      @MAN_CB;

      forever
        begin
          MAN_CB.tdata <= 0;
          MAN_CB.tvalid <= 0;
          MAN_CB.tlast <= 0;
	  
          wait(op_q.size() != 0);
	  
          cur_op = op_q.pop_front();
	  
          do begin
            $display("%s: (%t) manager operation %d %x", name, $time, cur_op.code.name, cur_op.data);
	    
            case (cur_op.code)
              WRITE: begin
                MAN_CB.tdata <= cur_op.data;
                MAN_CB.tvalid <= 1;
		MAN_CB.tlast <= cur_op.tlast;
                $display("%s: (%t) manager write data out (%x r: %d v: %d)", name, $time, cur_op.data, MAN_CB.tready, tvalid);
                @(MAN_CB iff tvalid == 1 && MAN_CB.tready == 1);
                $display("%s: (%t) manager write complete (%x r: %d v: %d)", name, $time, cur_op.data, MAN_CB.tready, tvalid);
              end
	      
              SYNC: -> cur_op.e;
            endcase
            cur_op = op_q.pop_front();
          end while(cur_op);
        end
    end
endmodule;
