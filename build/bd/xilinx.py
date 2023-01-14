from .pin import register_intf_pin
from .port import register_intf_port
from .ip import BDIP
from .axi import AXIInterconnect

_xilinx_vlnv_defs = {
    "BDDiffIO": "xilinx.com:interface:diff_analog_io_rtl:1.0",
    "BDDiffClock": "xilinx.com:interface:diff_clock_rtl:1.0",
    "BDSYSREF": "xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0",
    "BDAXIS": "xilinx.com:interface:axis_rtl:1.0",
    "BDAXIMM": "xilinx.com:interface:aximm_rtl:1.0",
    "BDUART": "xilinx.com:interface:uart_rtl:1.0",
    "BDI2C": "xilinx.com:interface:iic_rtl:1.0",
}

_xilinx_intf_pin_defs = { k+"Pin":v for k,v in _xilinx_vlnv_defs.items() }
_xilinx_intf_port_defs = { k+"Port":v for k,v in _xilinx_vlnv_defs.items() }

_xilinx_ip_defs = {
    "ClockWizard": "xilinx.com:ip:clk_wiz:6.0",
    "BDPSReset": "xilinx.com:ip:proc_sys_reset:5.0",
    "BDI2C": "xilinx.com:ip:axi_iic:2.1",
}

for name, vlnv in _xilinx_intf_pin_defs.items():
    globals()[name] = register_intf_pin(name, vlnv)

for name, vlnv in _xilinx_intf_port_defs.items():
    globals()[name] = register_intf_port(name, vlnv)

    
for name, vlnv in _xilinx_ip_defs.items():
    globals()[name] = BDIP.create_class(name, vlnv)
