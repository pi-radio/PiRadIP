from .cell import BDCell
from .registry import VLNVRegistry

class BDIP(BDCell, VLNVRegistry):
    def __init__(self, parent, name, d):
        super().__init__(parent, name)
        parent.make_active()
        self.cmd(f"create_bd_cell -type ip -vlnv {self.vlnv} {name}")
            
        if d is not None:
            self.set_property_list(d)
