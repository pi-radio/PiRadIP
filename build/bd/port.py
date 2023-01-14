from .obj import BDObj
from .registry import VLNVRegistry

class BDPortBase(BDObj):
    port=True
    def __init__(self, parent, name):
        super().__init__(parent, name)
        assert(self.parent is not None)
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

    

class BDProperty:
    def __init__(self, name, ro=False):
        self.name = name
        self.ro = ro
        
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return instance.get_property(self.name)

    def __set__(self, instance, value):
        if self.ro:
            raise AttributeError(f"Property {self.name} is read only")
        return instance.set_property(self.name, value)
        


    
class BDPort(BDPortBase):
    iostd = BDProperty("IOSTANDARD")
    pkg_pin = BDProperty("PACKAGE_PIN")
    
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
    def iostd(self):
        self.get_property("IOSTANDARD")
    
    @property
    def obj(self):
        return f"[get_bd_port {self.path}]"


class BDIntfPort(BDPortBase, VLNVRegistry):
    intf = True
    
    def __init__(self, parent, name, mode):
        super().__init__(parent, name)
        self.parent.ports[name] = self
        self.mode = mode
        
    def create(self):
        self.cmd(f"create_bd_intf_port -mode {self.mode} -vlnv {self.vlnv} {self.name}")
            
    @property
    def obj(self):
        return f"[get_bd_intf_port {self.path}]"

def register_intf_port(name, vlnv):
    return BDIntfPort.create_class(name, vlnv)

def create_port(parent, name, **kwargs):
    if "vlnv" in kwargs:
        return BDIntfPort.construct(kwargs["vlnv"], parent, name, kwargs["mode"])
    else:
        return BDPort(parent, name, **kwargs)
