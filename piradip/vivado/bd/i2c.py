import re
from functools import cached_property

from .pin import BDIntfPin
from .port import BDPortBase, BDIntfPort
from .ip import BDIP
from .buffer import IOBUF
from .tristate import TristatePin, TristatePort

class BDI2CVirtualPort(BDPortBase):
    @property
    def prefix(self):
        if self.intf_pin.name == "IIC":
            return self.intf_pin.parent.name + "_"
        return self.intf_pin.parent.name + "_" + self.intf_pin.name + "_"
    
    def __init__(self, intf_pin, parent):
        self.intf_pin = intf_pin
        super().__init__(parent, intf_pin.name + "_export")

        self.sda_in = intf_pin.sda
        self.scl_in = intf_pin.scl

        self.sda_out = self.sda_in.create_port(parent, self.prefix + "sda")
        self.scl_out = self.scl_in.create_port(parent, self.prefix + "scl")
        
@BDIntfPin.register
class BDI2CPin(BDIntfPin):
    vlnv = "xilinx.com:interface:iic_rtl:1.0"

    def __init__(self, parent, name, mode='Slave', enum_pins=False):
        assert enum_pins == True
        super().__init__(parent, name, mode, enum_pins)
        
    @cached_property
    def sda(self):
        return TristatePin(self.pins["sda_i"], self.pins["sda_o"], self.pins["sda_t"])
    
    @cached_property
    def scl(self):
        return TristatePin(self.pins["scl_i"], self.pins["scl_o"], self.pins["scl_t"])

    def export_as_port(self, parent):
        return BDI2CVirtualPort(self, parent)
        
    
@BDIntfPort.register
class BDI2CPort(BDIntfPort):
    vlnv = "xilinx.com:interface:iic_rtl:1.0"

@BDIP.register
class BDI2C(BDIP):
    vlnv = "xilinx.com:ip:axi_iic:2.1"

    def __init__(self, parent, name, p):
        super().__init__(parent, name, p)        
