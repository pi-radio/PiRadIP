package piradspi;
    localparam SPI_IP_MAGIC                 = 32'h91700591;
	localparam SPI_IP_VER                   = 32'h00000100;

	localparam regno_t REGISTER_DEVID       = 'h00;
	localparam regno_t REGISTER_VER         = 'h01;
    localparam regno_t REGISTER_CTRLSTAT    = 'h02;
    
    localparam int CTRLSTAT_ENABLE  = 0;
    localparam int CTRLSTAT_ERROR   = 1;
    localparam int CTRLSTAT_BUSY    = 2;
    localparam int CTRLSTAT_AUTOINC = 3;
    localparam int CTRLSTAT_INTR    = 4;
    localparam int CTRLSTAT_INTREN  = 5;
  
    localparam regno_t REGISTER_DEVSELECT   = 'h03;
    localparam regno_t REGISTER_PROFSELECT  = 'h04;
    localparam regno_t REGISTER_CMD_ID      = 'h05;
    
    localparam regno_t REGISTER_MOSIFIFO    = 'h06;
    localparam regno_t REGISTER_MISOFIFO    = 'h07;
    localparam regno_t REGISTER_CMPLCNT     = 'h08;
    localparam regno_t REGISTER_INTRACK     = 'h09;

    localparam regno_t REGISTER_TRIGGER     = 'h0F;

    localparam regno_t REGISTER_PROFBASE    = 'h10;
    localparam regno_t REGISTER_POLPHA      = 'h0;
    localparam regno_t REGISTER_SCLKDIV     = 'h1;
    localparam regno_t REGISTER_STARTWAIT   = 'h2;
    localparam regno_t REGISTER_CSNTOSCLK   = 'h3;
    localparam regno_t REGISTER_SCLKTOCSN   = 'h4;
    localparam regno_t REGISTER_XFERLEN     = 'h5;
    
    localparam regno_t REGISTER_PROFSIZE    = 'h8;   

    localparam integer WAIT_WIDTH      = 8;
    localparam integer CMD_ID_WIDTH    = 8;
    localparam integer XFER_LEN_WIDTH  = 16;
    localparam integer DEVICE_ID_WIDTH = 8;
    localparam integer MAGIC_WIDTH     = 8;

    localparam RESPONSE_MAGIC = 8'hAD;    

    typedef logic [WAIT_WIDTH-1:0] wait_t;
    typedef logic [CMD_ID_WIDTH-1:0] cmd_id_t;
    typedef logic [XFER_LEN_WIDTH-1:0] xfer_len_t;
    typedef logic [DEVICE_ID_WIDTH-1:0] dev_id_t;
    typedef logic [MAGIC_WIDTH-1:0] magic_t;

    typedef struct packed {
        logic       cpol;
        logic       cpha;
        cmd_id_t    id;
        dev_id_t    device;
        wait_t      sclk_cycles;
        wait_t      wait_start;
        wait_t      csn_to_sclk_cycles;
        wait_t      sclk_to_csn_cycles;        
        xfer_len_t  xfer_len;
    } command_t;
    
    localparam CMD_FIFO_WIDTH = 8*($bits(command_t)/8 + (($bits(command_t) & 3'h7) ? 1 : 0));
    
    typedef logic [CMD_FIFO_WIDTH-1:0] cmd_word_t;
    
    typedef struct packed {
        magic_t        magic;
        cmd_id_t       id;
    } response_t;
    
    typedef union packed {
        struct packed {
            logic [CMD_FIFO_WIDTH-$bits(command_t)-1:0] pad;
            command_t cmd;
        } c;
        cmd_word_t data;
    } command_u_t;

    function automatic logic [CMD_FIFO_WIDTH-1:0]  build_command(
        input dev_id_t dev,
        input xfer_len_t xfer_len,
        input cmd_id_t cmd_id,
        input logic cpol, 
        input logic cpha, 
        input wait_t sclk_cycles=1,
        input wait_t wait_start=1,
        input wait_t csn_to_sclk_cycles = 5,
        input wait_t sclk_to_csn_cycles = 5
        );
        
        command_u_t cmd;
        
        cmd.c.cmd.id = cmd_id;
        cmd.c.cmd.cpol = cpol;
        cmd.c.cmd.cpha = cpha;
        
        cmd.c.cmd.device = dev;
        cmd.c.cmd.sclk_cycles = sclk_cycles;
        cmd.c.cmd.wait_start = wait_start;
        cmd.c.cmd.csn_to_sclk_cycles = csn_to_sclk_cycles;
        cmd.c.cmd.sclk_to_csn_cycles = sclk_to_csn_cycles;
        cmd.c.cmd.xfer_len = xfer_len;
        cmd.c.pad = 0;
        
        return cmd.data;
    endfunction              

endpackage
