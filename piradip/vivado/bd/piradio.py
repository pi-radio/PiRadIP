from .pin import BDIntfPin
from .port import BDIntfPort
from .ip import BDIP

_piradio_ip_defs = {
    "AXISSampleInterleaver": "pi-rad.io:piradip:axis_sample_interleaver:1.0",
    "TriggerUnit": "pi-rad.io:piradip:piradip_trigger_unit:1.0",
    "PiRadSPI": "pi-rad.io:piradip:piradspi_ip:1.0",
    "AXIS_FIR7SYM_16WIDE": "pi-rad.io:piradip:piradio_16x4sym:1.0",
    "MTSClocking": "pi-rad.io:piradip:mts_clocking:1.0"
}

class Concat(BDIP):
    def __init__(self, n, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n = n
        self._i = 0

    def get_pin(self):
        assert self._i < self._n
        
        retval = self.pins[f"din{self._i}"]

        self._i += 1
        
        return retval

@BDIP.register
class Concat8(Concat):
    vlnv = "pi-rad.io:piradip:piradip_concat8:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)

    
@BDIP.register
class Concat16(Concat):
    vlnv = "pi-rad.io:piradip:piradip_concat16:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)
    
@BDIP.register
class Concat32(Concat):
    vlnv = "pi-rad.io:piradip:piradip_concat32:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)
    

class Slice(BDIP):
    def __init__(self, n, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._n = n
        self._i = 0

    def get_pin(self):
        assert self._i < self._n
        
        retval = self.pins[f"dout{self._i}"]

        self._i += 1
        
        return retval
    
@BDIP.register
class Slice8(Slice):
    vlnv = "pi-rad.io:piradip:piradip_slice8:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)

    
@BDIP.register
class Slice16(Slice):
    vlnv = "pi-rad.io:piradip:piradip_slice16:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)
    
@BDIP.register
class Slice32(Slice):
    vlnv = "pi-rad.io:piradip:piradip_slice32:1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(32, *args, **kwargs)


for name, vlnv in _piradio_ip_defs.items():
    globals()[name] = BDIP.create_class(name, vlnv)
