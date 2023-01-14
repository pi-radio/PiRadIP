from functools import cached_property
from collections import defaultdict

from .obj import bdactive, suffixize
from .net import BDNet, BDIntfNet
from .pin import create_pin
from .port import create_port



class BDConnector:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pin_map = dict()
        self.net_map = dict()
        self.cells = dict()
        
    @bdactive
    def create_net(self, intf, name):
        if not intf:
            net = BDNet(self, name)
            self.cmd(f"create_bd_net {net.path}")
        else:
            net = BDIntfNet(self, name)

        self.net_map[name] = net

        return net

    def assign_pin(self, pin, net):
        if net.parent == pin.parent:
            pin.inner_net = net
        else:
            pin.outer_net = net
            
        self.pin_map[pin] = net
        net.pins.append(pin)
        
    
    @bdactive
    def connect_non_intf_net(self, net, *pins):
        for p in pins:
            self.assign_pin(p, net)

        self.cmd(f"connect_bd_net -net {net.path} " + " ".join(p.obj for p in pins))

    @bdactive
    def connect_intf_net(self, net, *pins):
        assert len(net.pins) + len(pins) <= 2, f"{net.name}: Too many pins for an interface connection pins: {net.pins} args: {pins}"

        if len(pins) == 0:
            return

        for p in pins:
            self.assign_pin(p, net)
            
        if len(net.pins) < 2:
            return

        assert net.pins[0].vlnv == net.pins[1].vlnv, f"Inconsistent vlnv: need {net.pins[0].path} has {net.pins[0].vlnv}, {net.pins[1].path} has {net.pins[1].vlnv}"

        self.cmd(f"connect_bd_intf_net -intf_net {net.name} " + " ".join([p.obj for p in net.pins]))
        
    
    def connect_net(self, net, *pins):
        if net.intf:
            return self.connect_intf_net(net, *pins)
        else:
            return self.connect_non_intf_net(net, *pins)        
    
    def connect(self, *pins, name=None, debug=False):        
        intf = list(set([ p.intf for p in pins ]))

        assert len(intf) == 1, "Mix of interfaces and non-interface pins"

        intf = intf[0]
        
        nets = set(filter(lambda x: x.net, pins))

        assert len(nets) < 2, "Multiple nets specified.  TODO: try connecting anyway"

        pins = list(filter(lambda x: x.pin or x.port, pins))

        pin_nets = set([ p.get_ctx_net(self) for p in pins ]) - set([None])

        if debug:
            print(f"Nets: {nets}")
            print(f"Pins: {pins}")
            print(f"Pin nets: {pin_nets}")
        
        nets = list(nets | pin_nets)

        if debug:
            print(f"Unified nets: {nets}")

        assert len(nets) < 2, "Multiple already connected pins.  TODO: try connecting anyway"

        if len(nets):
            net = nets[0]
            assert name is None, "Can not rename nets"
        else:
            if name is None:
                if self.parent is not None:
                    name = f"net_{self.parent.name}_{pins[0].name}"
                else:
                    name = f"net_{pins[0].name}"
                    
                while name in self.net_map:
                    name = suffixize(name)
                
            net = self.create_net(intf, name)
            
        return self.connect_net(net, *pins)
                
    @bdactive
    def reexport(self, pin, name=None, debug=False):
        assert pin.parent != self

        desc = pin.desc

        if name is not None:
            desc["name"] = name
        
        if self.parent == None:
            # These should be ports
            new_pin = create_port(self, **desc)
        else:
            new_pin = create_pin(self, **desc)

        new_pin.create()

        if debug:
            print(f"REXEPORT: {self.path}: {pin}({pin.parent.path})<=>{new_pin}({new_pin.parent.path})")
            
        self.connect(pin, new_pin)

        return new_pin
        
