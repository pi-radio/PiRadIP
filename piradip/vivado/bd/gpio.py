from functools import cached_property

from .ip import BDIP
from .pin import BDIntfPin, all_pins
from .piradio import AXISSampleInterleaver

@BDIP.register
class GPIO(BDIP):
    vlnv = "xilinx.com:ip:axi_gpio:2.0"

    def __init__(self, parent, name, dual=False):
        if dual:
            super().__init__(parent, name, [ ("CONFIG.C_IS_DUAL", "1") ])
        else:
            super().__init__(parent, name, None)
        

    
