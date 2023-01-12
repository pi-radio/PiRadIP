from .pin import BDIntfPin
from .port import BDIntfPort
from .ip import BDIP
from .rfdc import RFDC

_xilinx_vlnv_defs = {
    "BDDiffIO": "xilinx.com:interface:diff_analog_io_rtl:1.0",
    "BDDiffClock": "xilinx.com:interface:diff_clock_rtl:1.0",
    "BDSYSREF": "xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0",
    "BDAXIS": "xilinx.com:interface:axis_rtl:1.0",
    "BDAXIMM": "xilinx.com:interface:aximm_rtl:1.0"
}

_xilinx_intf_pin_defs = { k+"Pin":v for k,v in _xilinx_vlnv_defs.items() }
_xilinx_intf_port_defs = { k+"Port":v for k,v in _xilinx_vlnv_defs.items() }

_xilinx_ip_defs = {
    "ClockWizard": "xilinx.com:ip:clk_wiz:6.0",
    "AXIInterconnect": "xilinx.com:ip:axi_interconnect:2.1"
}

for name, vlnv in _xilinx_intf_pin_defs.items():
    globals()[name] = BDIntfPin.create_class(name, vlnv)

for name, vlnv in _xilinx_intf_port_defs.items():
    globals()[name] = BDIntfPort.create_class(name, vlnv)

    
for name, vlnv in _xilinx_ip_defs.items():
    globals()[name] = BDIP.create_class(name, vlnv)

BDIP.registry[RFDC.vlnv] = RFDC
