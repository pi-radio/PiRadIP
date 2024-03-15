import re

from .ip import BDIP

@BDIP.register
class AXISDataWidthConverter(BDIP):
    vlnv = "xilinx.com:ip:axis_dwidth_converter:1.1"

@BDIP.register
class AXISClockConverter(BDIP):
    vlnv = "xilinx.com:ip:axis_clock_converter:1.1"
    
@BDIP.register
class AXISDataFifo(BDIP):
    vlnv = "xilinx.com:ip:axis_data_fifo:2.0"

@BDIP.register
class AXISRegisterSlice(BDIP):
    vlnv = "xilinx.com:ip:axis_register_slice:1.1"

@BDIP.register
class AXISBroadcaster(BDIP):
    vlnv = "xilinx.com:ip:axis_broadcaster:1.1"
