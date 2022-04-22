`timescale 1ns / 1ps

/*
 Register map
 
 Reg 00h: Control/Status
 Bit 0 - Enable(d)
 Bit 1 - Error
 Bit 2 - Busy
 Bit 3 - Autoincrement ID enable
 Bit 4 - Interrupt Asserted
 Bit 5 - Interrupt Enable
 Reg 01h: 
 
 --- Command Programming
 Reg 10h: Device Select
 Reg 11h: Profile Select
 Reg 12h: Command ID
 Reg 18h: MOSI FIFO
 Reg 19h: MISO FIFO
 Reg 1Fh: Trigger
 
 -- Profiles start at 20h
 Reg 0h: POL/PHA
 Reg 1h: SCLK div
 Reg 2h: Start wait cycles
 Reg 3h: CSN assert to SCLK cycles
 Reg 4h: SCLK to CSN deassert cycles
 Reg 5h: Transfer Length    
 */
package piradspi_pkg;
   localparam SPI_IP_MAGIC                 = 32'h91700591;
   localparam SPI_IP_VER                   = 32'h00000100;

   localparam integer REGISTER_DEVID       = 'h00;
   localparam integer REGISTER_VER         = 'h01;
   localparam integer REGISTER_CTRLSTAT    = 'h02;
   
   localparam int     CTRLSTAT_ENABLE    = 0;
   localparam int     CTRLSTAT_ERROR     = 1;
   localparam int     CTRLSTAT_BUSY      = 2;
   localparam int     CTRLSTAT_AUTOINC   = 3;
   localparam int     CTRLSTAT_INTR      = 4;
   localparam int     CTRLSTAT_INTREN    = 5;
   localparam int     CTRLSTAT_MOSIREADY = 6;
   localparam int     CTRLSTAT_MISOREADY = 7;
   
   localparam integer REGISTER_DEVSELECT   = 'h03;
   localparam integer REGISTER_PROFSELECT  = 'h04;
   localparam integer REGISTER_CMD_ID      = 'h05;
   
   localparam integer REGISTER_MOSIFIFO    = 'h06;
   localparam integer REGISTER_MISOFIFO    = 'h07;
   localparam integer REGISTER_CMPLCNT     = 'h08;
   localparam integer REGISTER_INTRACK     = 'h09;

   localparam integer REGISTER_TRIGGER     = 'h0F;

   localparam integer REGISTER_PROFBASE    = 'h10;
   localparam integer REGISTER_POLPHA      = 'h0;
   localparam integer REGISTER_SCLKDIV     = 'h1;
   localparam integer REGISTER_STARTWAIT   = 'h2;
   localparam integer REGISTER_CSNTOSCLK   = 'h3;
   localparam integer REGISTER_SCLKTOCSN   = 'h4;
   localparam integer REGISTER_XFERLEN     = 'h5;
   
   localparam integer REGISTER_PROFSIZE    = 'h8;   

   localparam integer MAGIC_WIDTH = 8;
   localparam integer CMD_ID_WIDTH = 8;
   localparam integer RESPONSE_MAGIC = 8'hAD;    
   localparam integer WAIT_WIDTH = 8;
   localparam integer XFER_LEN_WIDTH = 16;
   localparam integer  DEVICE_ID_WIDTH = 8;
   
   typedef logic [CMD_ID_WIDTH-1:0]    cmd_id_t;
   typedef logic [MAGIC_WIDTH-1:0]     magic_t;

   typedef logic [WAIT_WIDTH-1:0]      wait_t;
   typedef logic [XFER_LEN_WIDTH-1:0]  xfer_len_t;
   typedef logic [DEVICE_ID_WIDTH-1:0] dev_id_t;

   
   typedef struct                      packed {
      magic_t        magic;
      cmd_id_t       id;
   } response_t;
endpackage
