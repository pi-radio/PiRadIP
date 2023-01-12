from .obj import BDObj, bdactive
from .pin import BDIntfPin
from .port import BDIntfPort

class BD(BDObj):
    def __init__(self, vivado, name):
        super().__init__(None, name)
        self.vivado = vivado
        self.vivado.cmd(f"create_bd_design {name}")
        self._current = self
        self.name = name
        self.intf_ports = dict()
        self.ports = dict()

    @bdactive
    def connect(self, c1, c2):
        if isinstance(c1, BDIntfPort):
            assert(isinstance(c2, BDIntfPin))
            net_name = f"conn_{c1.name}_{c2.name}" if c1.name != c2.name else f"conn_{c1.name}"
            self.cmd(f"connect_bd_intf_net -intf_net {net_name} {c1.obj} {c2.obj}")
        else:
            print(type(c1).__name__)
            print(type(c2).__name__)
            raise Exception("Unable to connect these objects")

        
    def set_current(self, cell):
        if self._current != cell:
            self._current = cell
            self.cmd(f"current_bd_instance {cell.path}")
            
            
    def create_intf_port(self, name, mode, vlnv, d):
        if d is not None:
            self.cmd(f"set_property {get_property_dict(d)} [{cs}]")
        else:
            self.cmd(f"{cs}")

    def validate(self):
        self.cmd("validate_bd_design")
                
    def save(self):
        self.cmd("save_bd_design")

    def close(self):
        self.cmd(f"close_bd_design {self.name}")
        
