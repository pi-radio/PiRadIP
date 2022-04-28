`timescale 1ns / 1ps

module piradip_shift_sub #(
    parameter integer DATA_WIDTH = 32,
    parameter integer SHIFT_WIDTH = 6,
    parameter PIPELINE = 0,
    parameter RECURSIVE = 1
) (
    axis_simple.SUBORDINATE data_in,
    axis_simple.MANAGER data_out
);
  logic [SHIFT_WIDTH-1:0] shift;
  logic [ DATA_WIDTH-1:0] data;

  assign shift = data_in.tdata[DATA_WIDTH+:SHIFT_WIDTH];
  assign data  = data_in.tdata[0+:DATA_WIDTH];

  generate
    if (SHIFT_WIDTH == 1) begin
      assign data_in.tready  = data_out.tready;
      assign data_out.tdata  = shift[0] ? (data << 1) : data;
      assign data_out.tvalid = data_in.tvalid;
    end else begin
      axis_simple #(
          .WIDTH(DATA_WIDTH + SHIFT_WIDTH - 1)
      ) next_data (
          .clk(data_in.aclk),
          .resetn(data_in.aresetn)
      );

      if (RECURSIVE) begin
        piradip_shift_sub #(
            .DATA_WIDTH(DATA_WIDTH),
            .SHIFT_WIDTH(SHIFT_WIDTH - 1),
            .PIPELINE(PIPELINE)
        ) next_stage (
            .data_in (next_data.SUBORDINATE),
            .data_out(data_out)
        );
      end else begin
        assign data_out.tdata   = next_data.tdata;
        assign data_out.tvalid  = next_data.tvalid;
        assign data_out.tlast   = next_data.tlast;
        assign next_data.tready = data_out.tready;
      end

      logic [SHIFT_WIDTH-2:0] next_shift;
      assign next_shift = shift[SHIFT_WIDTH-2:0];

      if (PIPELINE) begin
        always @(posedge data_in.aclk) begin
          if (~data_in.aresetn) begin
            next_data.tvalid = 0;
            data_in.tready   = 0;
            next_data.tdata  = {{{SHIFT_WIDTH - 1} {1'b0}}, {{DATA_WIDTH} {1'b0}}};
          end else begin
            data_in.tready <= next_data.tready | ~next_data.tvalid;

            if (next_data.tvalid & next_data.tready) begin
              next_data.tvalid <= 0;
            end

            if (data_in.tvalid & data_in.tready) begin
              next_data.tvalid <= 1;
              next_data.tdata <= {
                next_shift, shift[SHIFT_WIDTH-1] ? (data << (1 << (SHIFT_WIDTH - 1))) : data
              };
            end
          end
        end
      end else begin
        assign data_in.tready = data_in.aresetn & next_data.tready;
        assign next_data.tdata = {
          next_shift, shift[SHIFT_WIDTH-1] ? (data << (1 << (SHIFT_WIDTH - 1))) : data
        };
        assign next_data.tvalid = data_in.tvalid;
      end
    end
  endgenerate
endmodule

module piradip_left_shift #(
    parameter integer DATA_WIDTH = 32,
    parameter SHIFT_WIDTH = $clog2(DATA_WIDTH) + 1,
    parameter PIPELINE = 0,
    parameter RECURSIVE = 1
) (
    axis_simple.SUBORDINATE data_in,
    axis_simple.MANAGER data_out
);

  genvar i, j;

  generate
    if (RECURSIVE) begin
      piradip_shift_sub #(
          .DATA_WIDTH(DATA_WIDTH),
          .SHIFT_WIDTH(SHIFT_WIDTH),
          .PIPELINE(PIPELINE)
      ) shifter (
          .data_in (data_in),
          .data_out(data_out)
      );
    end else begin
      logic tvalid[0:SHIFT_WIDTH];
      logic tready[0:SHIFT_WIDTH];
      logic tlast[0:SHIFT_WIDTH];
      logic [SHIFT_WIDTH+DATA_WIDTH-1:0] tdata[0:SHIFT_WIDTH+1];

      assign data_in.tready = tready[0];
      assign tvalid[0] = data_in.tvalid;
      assign tlast[0] = data_in.tlast;
      assign tdata[0] = data_in.tdata;

      assign tready[SHIFT_WIDTH] = data_out.tready;
      assign data_out.tvalid = tvalid[SHIFT_WIDTH];
      assign data_out.tlast = tvalid[SHIFT_WIDTH];
      assign data_out.tdata = tdata[SHIFT_WIDTH][DATA_WIDTH-1:0];

      for (i = 0; i < SHIFT_WIDTH; i++) begin
        axis_simple #(
            .WIDTH(SHIFT_WIDTH + DATA_WIDTH - i)
        ) sub_in (
            .clk(data_in.aclk),
            .resetn(data_in.aresetn)
        );
        axis_simple #(
            .WIDTH(SHIFT_WIDTH + DATA_WIDTH - i - 1)
        ) sub_out (
            .clk(data_in.aclk),
            .resetn(data_in.aresetn)
        );

        assign sub_in.tvalid = tvalid[i];
        assign tready[i] = sub_in.tready;
        assign sub_in.tlast = tlast[i];
        assign sub_in.tdata = tdata[i];

        assign tvalid[i+1] = sub_out.tvalid;
        assign sub_out.tready = tready[i+1];
        assign tlast[i+1] = sub_out.tlast;
        assign tdata[i+1] = sub_out.tdata;

        piradip_shift_sub #(
            .DATA_WIDTH(DATA_WIDTH),
            .SHIFT_WIDTH(SHIFT_WIDTH - i),
            .PIPELINE(PIPELINE),
            .RECURSIVE(0)
        ) shifter (
            .data_in (sub_in.SUBORDINATE),
            .data_out(sub_out.MANAGER)
        );
      end
    end
  endgenerate
endmodule
