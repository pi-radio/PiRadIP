import sys

from .cell import BDCell
from .pin import create_pin
from .registry import VLNVRegistry

class BDIP(BDCell, VLNVRegistry):
    ip = True

    def __init__(self, parent, name, d):
        super().__init__(parent, name)
        parent.make_active()
        self.cmd(f"create_bd_cell -type ip -vlnv {self.vlnv} {name}", timeout=120)
        
        if d is not None:
            self.set_property_list(d)

        self.enumerate_pins()

        parent.cells[self.name]=self

    def apply_board_preset(self):
        self.cmd(f"apply_bd_automation -rule {self.bd_automation} -config {{ apply_board_preset \"1\" }}  {self.obj}")
        self.enumerate_pins()
                    
