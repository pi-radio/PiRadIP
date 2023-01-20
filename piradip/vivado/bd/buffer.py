import re

from .ip import BDIP

@BDIP.register
class UtilityBuffer(BDIP):
    vlnv = "xilinx.com:ip:util_ds_buf:2.2"

    def __init__(self, parent, name, d):
        super().__init__(parent, name, d)

class IOBUF(UtilityBuffer):
    def __init__(self, parent, name, width=1):
        super().__init__(parent, name, { "CONFIG.C_BUF_TYPE": "IOBUF", "CONFIG.C_SIZE": width })
