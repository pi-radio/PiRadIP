from .obj import BDObj
from .connector import BDConnector
from .port import BDIntfPort, BDPort

class BD(BDConnector, BDObj):
    hier = True
    root = True
    
    extern_intf_type = BDIntfPort
    extern_pin_type = BDPort

    def __init__(self, vivado, name):
        super().__init__(None, name)
        self.vivado = vivado
        self.vivado.cmd(f"create_bd_design {name}")
        self._current = self
        self.name = name
        self.intf_ports = dict()
        self.ports = dict()

    @property
    def parent(self):
        return None
        
    def get_current(self):
        return self._current
        
    def set_current(self, cell):
        if self._current != cell:
            self._current = cell
            if cell is not None:
                self.cmd(f"current_bd_instance {cell.path}")
                
    def validate(self):
        self.cmd("validate_bd_design")
                
    def save(self):
        self.cmd("save_bd_design")

    def close(self):
        self.cmd(f"close_bd_design {self.name}")
        
