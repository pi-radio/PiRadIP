from functools import cached_property

from .obj import BDObj

class BDNet(BDObj):
    net = True
    
    def __hash__(self):
        return hash(self.path)

    def __init__(self, parent, name):
        super().__init__(parent, name)
        self.pins = list()
            
    def connect(self, *args):
        self.parent.connect_net(self, *args)
        return self


    @property
    def desc(self):
        return { i: getattr(self, i) for i in [ 'name', 'left', 'right' ] }
    
    @property
    def left(self):
        v = self.get_property("LEFT")

        if v == '':
            return 0
        
        return int(v)

    @property
    def right(self):
        v = self.get_property("RIGHT")

        if v == '':
            return 0
        
        return int(v)

    @property
    def obj(self):
        return f"[get_bd_nets {{{self.path}}}]"
    
    def __repr__(self):
        return f"<|NET: {self.name}|>"
    
    def assign_pin(self, pin):
        if self.parent == pin.parent:
            pin.inner_net = self
        else:
            pin.outer_net = self

class BDIntfNet(BDNet):
    intf = True

    def __init__(self, parent, name):
        super().__init__(parent, name)

    @property
    def obj(self):
        return f"[get_bd_intf_nets {{{self.path}}}]"
