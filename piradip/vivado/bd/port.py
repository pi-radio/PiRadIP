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

    @property
    def phys_name(self):
        return self.name    

    def set_phys(self, ball, iostd="LVCMOS18"):
        assert ball not in self.parent.phys_map, f"Ball {ball} previously assigned to {self.parent.phys_map[ball].name}"
        self.ball = ball
        self.iostd = iostd
        self.parent.phys_map[ball] = self
        self.parent.port_phys[self.phys_name] = { 'ball': ball, 'iostd': iostd }

    def set_diff_term(self, term):
        self.parent.port_phys[self.phys_name]['diff_term'] = term
    
class BDPort(BDPortBase):    
    def __init__(self, parent, name, direction="I", pin_type="data", left=0, right=0, intf=False):
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

    @classmethod
    def create_from_bd(cls, parent, path):
        props = parent.cmd(f"list_property [get_bd_pin {path}]").split()
        
        d = dict()

        for p in props:
            d[p] = parent.cmd(f"get_property {p} [get_bd_pin {path}]")

        left = int(d["LEFT"]) if d["LEFT"] != "" else 0
        right = int(d["RIGHT"]) if d["RIGHT"] != "" else 0
        pin_type = d["TYPE"]
        intf = True if d["INTF"] == "TRUE" else False
        direction = d["DIR"]
        name = d["NAME"]

        return BDPort(parent, name, direction=direction, pin_type=pin_type, left=left, right=right, intf=intf)
        
        
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

    @classmethod
    def create_from_bd(cls, parent, path):
        mode = parent.cmd(f"get_property MODE [get_bd_intf_port {path}]")

        retval = BDIntfPort(parent, path.split("/")[-1], mode)

        v = parent.cmd(f"get_bd_ports -of_objects {retval.obj}").split()

        retval.ports = {}
        
        for path in v:
            port = BDPort.create_from_bd(parent, path)
            retval.ports[port.name] = port

        return retval
        
    def create(self):
        #print(f"Creating INTF port: create_bd_intf_port -mode {self.mode} -vlnv {self.vlnv} {self.name}")
        self.parent.make_active()
        result = self.cmd(f"create_bd_intf_port -mode {self.mode} -vlnv {self.vlnv} {self.name}")

        #s = f"get_bd_ports -of_objects {self.obj}"

        v = self.cmd(f"get_bd_pins -of_objects {self.obj}").split()
                
        self.ports = {}
        
        for path in v:
            port = BDPort.create_from_bd(path)

            self.ports[port.name] = port
        
    @property
    def obj(self):
        return f"[get_bd_intf_ports {self.path}]"

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
