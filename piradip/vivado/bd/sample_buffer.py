import math

from .pin import BDIntfPin
from .port import BDIntfPort
from .ip import BDIP

def clog2(x):
    return int(math.ceil(math.log2(x)))


@BDIP.register
class SampleBufferIn(BDIP):
    vlnv = "pi-rad.io:piradip:axis_sample_buffer_in:1.0"

    def __init__(self, parent, name, stream_width, nwords, ultra=False):
        addr_width = clog2(nwords) + 2

        print(f"nwords: {nwords}")
        print(f"addr_width: {addr_width}")
        
        super().__init__(parent, name,
                         {
                             "CONFIG.NWORDS": nwords, 
                             "CONFIG.C_AXIMM_ADDR_WIDTH": addr_width,
                             "CONFIG.STREAM_IN_WIDTH": stream_width,
                             "CONFIG.MEMORY_TYPE": 'ultra' if ultra else 'auto'
                         })                 

@BDIP.register
class SampleBufferOut(BDIP):
    vlnv = "pi-rad.io:piradip:axis_sample_buffer_out:1.0"

    def __init__(self, parent, name, stream_width, nwords, ultra=False):
        addr_width = clog2(nwords) + 2

        print(f"addr_width: {addr_width}")
        
        super().__init__(parent, name,
                         {
                             "CONFIG.NWORDS": nwords, 
                             "CONFIG.C_AXIMM_ADDR_WIDTH": addr_width,
                             "CONFIG.STREAM_OUT_WIDTH": stream_width,
                             "CONFIG.MEMORY_TYPE": 'ultra' if ultra else 'auto'
                         })                 
