from .obj import *
from .registry import VLNVRegistry

class BDPin(BDObj):
    def __init__(self, parent, name, direction="I", pin_type="io"):
        super().__init__(parent, name)
        assert(self.parent is not None)
        self.parent.pins[name]= self
        self.direction = direction
        self.pin_type = pin_type

    def create(self):
        self.cmd("create_bd_pin -dir {self.direction} -type {self.pin_type} {self.name}")
            
    @property
    def obj(self):
        return f"[get_bd_pin {self.path}]"


class BDIntfPin(BDObj, VLNVRegistry):    
    def __init__(self, parent, name, mode='Slave'):
        super().__init__(parent, name)
        assert(self.parent is not None)
        self.parent.intf_pins[name]= self
        self.mode = mode

    def __repr__(self):
        return f"<|PIN: {self.name} {self.vlnv}|>"

    def create(self):
        self.cmd(f"create_bd_intf_pin -mode {self.mode} -vlnv {self.vlnv} {self.name}")
            
    @property
    def obj(self):
        return f"[get_bd_intf_pin {self.path}]"
