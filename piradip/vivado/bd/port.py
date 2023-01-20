from .obj import BDObj
from .registry import VLNVRegistry

from piradip.vivado.property import VivadoProperty

class BDPortBase(BDObj):
    port=True
    def __init__(self, parent, name):
        super().__init__(parent, name)
        assert(self.parent is not None)
        if not self.virtual:
            self.parent.ports[name] = self
        self.inner_net = None

    def get_ctx_net(self, o):
        assert o == self.parent, "Bad context for port"
        return self.inner_net

    @property
    def connected(self):
        if self.inner_net is not None:
            if len(self.inner_net.pins) > 1:
                return True
        return False

    def set_phys(self, ball, iostd="LVCMOS18"):
        self.parent.port_phys[self.name] = (ball, iostd)
    
    
class BDPort(BDPortBase):
    iostd = VivadoProperty("IOSTANDARD")
    pkg_pin = VivadoProperty("PACKAGE_PIN")
    
    def __init__(self, parent, name, direction="I", pin_type="io", left=0, right=0, intf=False):
        super().__init__(parent, name)
        self.direction = direction
        self.pin_type = pin_type
        self.left = left
        self.right = right
        
    def create(self):
        self.cmd(f"create_bd_port -dir {self.direction} -type {self.pin_type} {self.name}")
        return self
    
    @property
    def obj(self):
        return f"[get_bd_port {self.path}]"

    def __getitem__(self, n):
        if not isinstance(n, int) or n > self.left or n < self.right:
            raise IndexError(f"{n} is an invalid index")

        return BDPortSlice(self, n)

class BDPortSlice(BDPortBase):
    virtual = True
    
    def __init__(self, port, n):
        super().__init__(port.parent, f"{port.name}[{n}]")
        self.port = port
        self.n = n

    @property
    def obj(self):
        return f"[get_bd_port {self.path}]"
    
class BDIntfPort(BDPortBase, VLNVRegistry):
    intf = True
    
    def __init__(self, parent, name, mode):
        super().__init__(parent, name)
        self.mode = mode
        
    def create(self):
        self.cmd(f"create_bd_intf_port -mode {self.mode} -vlnv {self.vlnv} {self.name}")
            
    @property
    def obj(self):
        return f"[get_bd_intf_port {self.path}]"

    def dump_ports(self):
        ports = self.cmd(f"get_bd_ports -of_object {self.obj}").split()

        for p in ports:
            print(p)

    
def register_intf_port(name, vlnv):
    return BDIntfPort.create_class(name, vlnv)

def create_port(parent, name, **kwargs):
    if "vlnv" in kwargs:
        return BDIntfPort.construct(kwargs["vlnv"], parent, name, kwargs["mode"])
    else:
        return BDPort(parent, name, **kwargs)
