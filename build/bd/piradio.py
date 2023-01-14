from .pin import BDIntfPin
from .port import BDIntfPort
from .ip import BDIP

_piradio_ip_defs = {
    "AXISSampleBufferIn": "pi-rad.io:piradip:axis_sample_buffer_in:1.0",
    "AXISSampleBufferOut": "pi-rad.io:piradip:axis_sample_buffer_out:1.0",
    "AXISSampleInterleaver": "pi-rad.io:piradip:axis_sample_interleaver:1.0",
    "Slice32": "pi-rad.io:piradip:piradip_slice32:1.0",
    "TriggerUnit": "pi-rad.io:piradip:piradip_trigger_unit:1.0",
    "PiRadSPI": "pi-rad.io:piradip:piradspi_ip:1.0",
}

for name, vlnv in _piradio_ip_defs.items():
    globals()[name] = BDIP.create_class(name, vlnv)
