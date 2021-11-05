package piradspi;
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
