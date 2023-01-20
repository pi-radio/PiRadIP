import sys

from .cell import BDCell
from .pin import create_pin
from .registry import VLNVRegistry

class BDIP(BDCell, VLNVRegistry):
    ip = True

    def __init__(self, parent, name, d):
        super().__init__(parent, name)
        parent.make_active()
        self.cmd(f"create_bd_cell -type ip -vlnv {self.vlnv} {name}")
        
        if d is not None:
            self.set_property_list(d)

        self.enumerate_pins()

        parent.cells[self.name]=self

    def apply_board_preset(self):
        self.cmd(f"apply_bd_automation -rule {self.bd_automation} -config {{ apply_board_preset \"1\" }}  {self.obj}")
        self.enumerate_pins()
                    
    def enumerate_pins(self):
        self.pins = dict()
        
        intf_pins = self.cmd(f"get_bd_intf_pins -quiet -of {self.obj}").split()

        if len(intf_pins):
            # CLASS CONFIG.CAN_DEBUG CONFIG.FREQ_HZ LOCATION MODE NAME PATH TYPE VLNV

            names = self.cmd(f"get_property NAME [get_bd_intf_pins -of {self.obj}]").split()
            modes = self.cmd(f"get_property MODE [get_bd_intf_pins -of {self.obj}]").split()
            vlnvs = self.cmd(f"get_property VLNV [get_bd_intf_pins -of {self.obj}]").split()

            for name, mode, vlnv in zip(names, modes, vlnvs):
                create_pin(self, name, mode=mode, vlnv=vlnv, enum_pins=True)

        pins = self.cmd(f"get_bd_pins -quiet -filter {{INTF==\"\"}} -of {self.obj}").split()

        if len(pins):
            def vb(x):
                if x == "TRUE":
                    return True
                return False
            
            def vr(x):
                if x == "{}":
                    return 0
                return int(x)
            
            attrs = {
                'name': self.cmd(f"get_property NAME [get_bd_pins -of {self.obj}]").split(),
                'intf': map(vb, self.cmd(f"get_property INTF [get_bd_pins -of {self.obj}]").split()),
                'direction': self.cmd(f"get_property DIR [get_bd_pins -of {self.obj}]").split(),
                'pin_type': self.cmd(f"get_property TYPE [get_bd_pins -of {self.obj}]").split(),
                'left': map(vr, self.cmd(f"get_property LEFT [get_bd_pins -of {self.obj}]").split()),
                'right': map(vr, self.cmd(f"get_property RIGHT [get_bd_pins -of {self.obj}]").split())
            }

            for i in [ dict(zip(attrs, t)) for t in zip(*attrs.values()) ]:
                create_pin(self, **i)
