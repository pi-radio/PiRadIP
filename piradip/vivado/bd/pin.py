from .obj import *
from .registry import VLNVRegistry

class BDPinBase(BDObj):
    pin = True
    
    def __hash__(self):
        return hash(self.path)
    
    def __init__(self, parent, name):
        assert(parent is not None)
        assert(name is not None)
        
        super().__init__(parent, name)
        self.parent.pins[name]= self
        self.outer_net = None

        if self.parent.hier:
            self.inner_net = None

    def get_ctx_net(self, o):
        if o == self.parent:
            return self.inner_net
        elif o == self.parent.parent:
            return self.outer_net
        else:
            raise Exception("Uknown context...")

    @property
    def connected(self):
        if hasattr(self, "inner_net") and self.inner_net is not None:
            if len(self.inner_net.pins) > 1:
                return True
        if self.outer_net is not None:
            if len(self.outer_net.pins) > 1:
                return True
        return False
        
    def connect(self, other, **kwargs):
        if self.parent.hier:           
            self.parent.connect(self, other, **kwargs)
        else:
            self.parent.parent.connect(self, other, **kwargs)

    def create_net(self, name=None):
        if name is None:
            name = f"net_{self.parent.name}_{self.name}"

        if self.parent.hier:
            net = self.parent.create_net(self.intf, name)
        else:
            net = self.parent.parent.create_net(self.intf, name)

        net.connect(self)

        return net
            
class BDPin(BDPinBase):
    def __init__(self, parent, name, direction="I", pin_type="data", left=0, right=0, intf=False):
        super().__init__(parent, name)
        assert(self.parent is not None)

        assert pin_type in [ "clk", "ce", "data", "intr", "rst", "undef" ], f"Invalid pin type: {pin_type}"
        
        self.direction = direction
        self.pin_type = pin_type
        self.subpin = intf
        self.left = left
        self.right = right

    @property
    def desc(self):
        return { i: getattr(self, i) for i in [ 'name', 'direction', 'pin_type', 'left', 'right', 'intf' ] }
        
    def __repr__(self):
        if self.left != self.right:
            return f"<|PIN: {self.name}[{self.right}:{self.left}] {self.pin_type}|>"
        return f"<|PIN: {self.name} {self.pin_type}|>"
        
    def create(self):
        self.parent.make_active()
        self.cmd(f"create_bd_pin -dir {self.direction} -type {self.pin_type} {self.name}")
        return self

            
    @property
    def obj(self):
        return f"[get_bd_pin {self.path}]"
    
class BDIntfPin(BDPinBase, VLNVRegistry):
    intf = True
    
    def __init__(self, parent, name, mode='Slave', enum_pins=False):
        super().__init__(parent, name)
        self.mode = mode
        self.pins = dict()
        self.pin_type = "intf"

        if enum_pins:
            self.enumerate_pins()
            
    def enumerate_pins(self):
        q = f"[get_bd_pins -of_object {self.obj}]"
        
        def vb(x):
            if x == "TRUE":
                return True
            return False
        
        def vr(x):
            if x == "{}":
                return 0
            return int(x)
        
        
        attrs = {
            'name': self.cmd(f"get_property NAME {q}").split(),
            'intf': map(vb, self.cmd(f"get_property INTF {q}").split()),
            'direction': self.cmd(f"get_property DIR {q}").split(),
            'pin_type': self.cmd(f"get_property TYPE {q}").split(),
            'left': map(vr, self.cmd(f"get_property LEFT {q}").split()),
            'right': map(vr, self.cmd(f"get_property RIGHT {q}").split())
        }

        for i in [ dict(zip(attrs, t)) for t in zip(*attrs.values()) ]:
            self.pins[i["name"]] = create_pin(self.parent, **i)
        
                
    @property
    def desc(self):
        return { i: getattr(self, i) for i in [ 'name', 'vlnv', 'mode' ] }

        
    def __repr__(self):
        return f"<|PIN: {self.name} {self.vlnv}|>"

    def create(self):
        self.parent.make_active()
        self.cmd(f"create_bd_intf_pin -mode {self.mode} -vlnv {self.vlnv} {self.name}")
        return self

    @property
    def other(self):
        assert self.outer_net is not None, f"Interface is not connected {self.parent.name}/{self.name}"
        assert len(self.outer_net.pins) == 2
        assert not self.parent.hier

        l = self
        p = list(filter(lambda x: x != self, self.outer_net.pins))[0]

        while not p.parent.ip:
            if l in p.outer_net.pins:
                l = p
                p = list(filter(lambda x: x != self, p.inner_net.pins))[0]
            else:
                l = p
                p = list(filter(lambda x: x != self, p.outer_net.pins))[0]

        return p
            
    @property
    def obj(self):
        return f"[get_bd_intf_pin {self.path}]"

    def dump_pins(self):
        pins = self.cmd(f"get_bd_pins -of_object {self.obj}").split()

        for p in pins:
            print(p)

def register_intf_pin(name, vlnv):
    return BDIntfPin.create_class(name, vlnv)

allowed_intf_args = { "vlnv", "mode", "enum_pins" }

def create_pin(parent, name, **kwargs):
    if "vlnv" in kwargs:
        vlnv = kwargs.pop("vlnv")        
        assert len(kwargs.keys() - allowed_intf_args) == 0
        
        return BDIntfPin.construct(vlnv, parent, name, **kwargs)
    else:
        assert "mode" not in kwargs
        return BDPin(parent, name, **kwargs)
    
def all_pins(l, p):
    return [ i.pins[p] for i in l ]
