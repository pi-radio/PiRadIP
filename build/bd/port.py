from .obj import BDObj
from .registry import VLNVRegistry

class BDIntfPort(BDObj, VLNVRegistry):
    def __init__(self, parent, name, mode):
        super().__init__(parent, name)
        self.parent.intf_ports[name] = self
        self.mode = mode
        
    def create(self):
        self.cmd(f"create_bd_intf_port -mode {self.mode} -vlnv {self.vlnv} {self.name}")
            
    @property
    def obj(self):
        return f"[get_bd_intf_port {self.path}]"
