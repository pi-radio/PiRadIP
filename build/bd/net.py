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

    def assign_pin(self, pin):
        if self.parent == pin.parent:
            pin.inner_net = self
        else:
            pin.outer_net = self

class BDIntfNet(BDNet):
    intf = True

    def __init__(self, parent, name):
        super().__init__(parent, name)
        
        
