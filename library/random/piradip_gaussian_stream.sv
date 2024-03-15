
`timescale 1 ns / 1 ps

	module AXIGaussianStream_v1_0 #
	(
		// Users to add parameters here

		// User parameters ends
		// Do not modify the parameters beyond this line


		// Parameters of Axi Slave Bus Interface S00_AXIS
		parameter integer AXIS_TDATA_WIDTH	= 256,
		parameter integer N_RAND_STREAMS = 16
	)
	(
		input wire  axis_aclk,
		input wire  axis_aresetn,

		// Ports of Axi Slave Bus Interface S00_AXIS
		output wire  s00_axis_tready,
		input wire [AXIS_TDATA_WIDTH-1 : 0] s00_axis_tdata,
		input wire  s00_axis_tvalid,

		// Ports of Axi Master Bus Interface M00_AXIS
		output wire  m00_axis_tvalid,
		output reg [AXIS_TDATA_WIDTH-1 : 0] m00_axis_tdata,
		input wire  m00_axis_tready
	);
    localparam WIDTH = AXIS_TDATA_WIDTH / 16;
    localparam LOG_RAND_STREAMS = $clog2(N_RAND_STREAMS);
    localparam IN_WIDTH = (WIDTH - LOG_RAND_STREAMS);
    localparam LHCA_WIDTH=N_RAND_STREAMS * IN_WIDTH;
    localparam D = (LHCA_WIDTH == 8) ? 8'h06 :
           (LHCA_WIDTH == 16) ? 16'h4001 :
           (LHCA_WIDTH == 32) ? 32'h00004001 :
           (LHCA_WIDTH == 64) ? 64'h00000000_00000014 :
           (LHCA_WIDTH == 128) ? 128'h2000_0001 :
           (LHCA_WIDTH == 192) ? 192'h00008000_00000000_00000000_00000004 :
           (LHCA_WIDTH == 256) ? 256'h10000000_00000000_00000000_00000001 : 0;
       
    genvar i;
    
    for (i = 0; i < AXIS_TDATA_WIDTH/16; i=i+1)
    begin
        integer j;
        
        reg [LHCA_WIDTH-1:0] lhca;
        
        always @(posedge axis_aclk)
        begin
            if (~axis_aresetn) begin
                lhca <= {LHCA_WIDTH{1'b0}};
            end else begin
                lhca <= {IN_WIDTH{s00_axis_tdata[16*i+:16]}} ^ (lhca & D) ^ { 1'b0, lhca[LHCA_WIDTH-1:2] } ^ { lhca[LHCA_WIDTH-2:0], 1'b0 };
            end

            m00_axis_tdata[16*i+:16] = 0;
            
            for (j = 0; j < N_RAND_STREAMS; j = j + 1)
            begin
                m00_axis_tdata[16*i+:16] = m00_axis_tdata[16*i+:16] + lhca[IN_WIDTH*j+:IN_WIDTH];
            end

            m00_axis_tdata[16*i+:16] = m00_axis_tdata[16*i+:16] ^ 16'h8000;
        end 
    end

    assign s00_axis_tready = 1;
    assign m00_axis_tvalid = 1;
                        
	// User logic ends

endmodule
