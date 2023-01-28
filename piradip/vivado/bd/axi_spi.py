import re
from functools import cached_property

from .pin import BDIntfPin
from .port import BDPortBase, BDIntfPort
from .ip import BDIP
from .buffer import IOBUF

from piradip.vivado.property import VivadoProperty

@BDIP.register
class AXI_SPI(BDIP):
    vlnv = "xilinx.com:ip:axi_quad_spi:3.2"

    nslaves = VivadoProperty("CONFIG.C_NUM_SS_BITS")

    def __init__(self, parent, name, d):
        super().__init__(parent, name, d)
    
        self.aximm_overrides = {
            'AXI_LITE': {
                'clk': self.pins['s_axi_aclk'],
                'rst': self.pins['s_axi_aresetn']
            }
        }
        

