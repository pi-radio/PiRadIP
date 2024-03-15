from .pin import register_intf_pin
from .port import register_intf_port
from .ip import BDIP
from .axi import AXIInterconnect
from .buffer import UtilityBuffer, IOBUF
from .i2c import BDI2CPin, BDI2CPort, BDI2C

_xilinx_vlnv_defs = {
    "BDDiffIO": "xilinx.com:interface:diff_analog_io_rtl:1.0",
    "BDDiffClock": "xilinx.com:interface:diff_clock_rtl:1.0",
    "BDSYSREF": "xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0",
    "BDAXIS": "xilinx.com:interface:axis_rtl:1.0",
    "BDAXIMM": "xilinx.com:interface:aximm_rtl:1.0",
    "BDUART": "xilinx.com:interface:uart_rtl:1.0",
    "BDGPIO": "xilinx.com:interface:gpio_rtl:1.0",
    "BDSPI": "xilinx.com:interface:spi_rtl:1.0"
}

_xilinx_intf_pin_defs = { k+"Pin":v for k,v in _xilinx_vlnv_defs.items() }
_xilinx_intf_port_defs = { k+"Port":v for k,v in _xilinx_vlnv_defs.items() }

_xilinx_ip_defs = {
    "ClockWizard": "xilinx.com:ip:clk_wiz:6.0",
    "BDPSReset": "xilinx.com:ip:proc_sys_reset:5.0",
    "BDConcat": "xilinx.com:ip:xlconcat:2.1",
    "JTAGtoAXI": "xilinx.com:ip:jtag_axi:1.2",
    "UtilDSBuf": "xilinx.com:ip:util_ds_buf",
    "Constant": "xilinx.com:ip:xlconstant:1.1"
}

for name, vlnv in _xilinx_intf_pin_defs.items():
    globals()[name] = register_intf_pin(name, vlnv)

for name, vlnv in _xilinx_intf_port_defs.items():
    globals()[name] = register_intf_port(name, vlnv)

    
for name, vlnv in _xilinx_ip_defs.items():
    globals()[name] = BDIP.create_class(name, vlnv)


class IBUFDS(UtilDSBuf):
    def __init__(self, parent, name, props={}):
        props["CONFIG.C_BUF_TYPE"] = "IBUFDS"
        super().__init__(parent, name, props)

class BUFG(UtilDSBuf):
    def __init__(self, parent, name, props={}):
        props["CONFIG.C_BUF_TYPE"] = "BUFG"
        super().__init__(parent, name, props)

@BDIP.register
class BDVectorLogic(BDIP):
    vlnv = "xilinx.com:ip:util_vector_logic:2.0"

    def __init__(self, parent, name, props={}):
        super().__init__(parent, name, props)


class BDNot(BDVectorLogic):
    def __init__(self, parent, name, width=1):
         super().__init__(parent, name, { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": str(width) })

class BDAnd(BDVectorLogic):
    def __init__(self, parent, name, width=1):
         super().__init__(parent, name, { "CONFIG.C_OPERATION": "and", "CONFIG.C_SIZE": str(width) })

class BDOr(BDVectorLogic):
    def __init__(self, parent, name, width=1):
         super().__init__(parent, name, { "CONFIG.C_OPERATION": "or", "CONFIG.C_SIZE": str(width) })
         
class BDXor(BDVectorLogic):
    def __init__(self, parent, name, width=1):
         super().__init__(parent, name, { "CONFIG.C_OPERATION": "xor", "CONFIG.C_SIZE": str(width) })
