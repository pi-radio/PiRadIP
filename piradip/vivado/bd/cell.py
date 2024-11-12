from .obj import BDObj
from .pin import create_pin

class BDCell(BDObj):
    def __init__(self, parent, name):
        super().__init__(parent, name)
        if self.parent is not None:
            self.parent.cells[name] = self
        self.pins = dict()
        
    @property
    def obj(self):
        return f"[get_bd_cell {self.path}]"

    def dump_pins(self):
        for k, p in self.pins.items():
            if p.intf:
                print(f"{self.name}: pin: {k} {p.vlnv}")
            else:
                print(f"{self.name}: pin: {k}")

    @property
    def clk_pins(self):
        return filter(lambda x: x.pin_type == 'clk', self.pins.values())

    @property
    def intf_pins(self):
        return filter(lambda x: x.pin_type == 'intf', self.pins.values())
    
    @property
    def rst_pins(self):
        return filter(lambda x: x.pin_type == 'rst', self.pins.values())
    
    def enumerate_pins(self):
        self.pins = dict()
        
        intf_pins = self.cmd(f"get_bd_intf_pins -quiet -of {self.obj}").split()

        print(intf_pins)
        
        if len(intf_pins):
            # CLASS CONFIG.CAN_DEBUG CONFIG.FREQ_HZ LOCATION MODE NAME PATH TYPE VLNV

            names = self.cmd(f"get_property NAME [get_bd_intf_pins -of {self.obj}]").split()
            modes = self.cmd(f"get_property MODE [get_bd_intf_pins -of {self.obj}]").split()
            vlnvs = self.cmd(f"get_property VLNV [get_bd_intf_pins -of {self.obj}]").split()

            for name, mode, vlnv in zip(names, modes, vlnvs):
                create_pin(self, name, mode=mode, vlnv=vlnv, enum_pins=True)
                
        pins = self.cmd(f"get_bd_pins -quiet -filter {{INTF==\"\"}} -of {self.obj}").split()

        if len(pins):
            def vb(x):
                if x == "TRUE":
                    return True
                return False
            
            def vr(x):
                if x == "{}":
                    return 0
                return int(x)
            
            attrs = {
                'name': self.cmd(f"get_property NAME [get_bd_pins -of {self.obj}]").split(),
                'intf': map(vb, self.cmd(f"get_property INTF [get_bd_pins -of {self.obj}]").split()),
                'direction': self.cmd(f"get_property DIR [get_bd_pins -of {self.obj}]").split(),
                'pin_type': self.cmd(f"get_property TYPE [get_bd_pins -of {self.obj}]").split(),
                'left': map(vr, self.cmd(f"get_property LEFT [get_bd_pins -of {self.obj}]").split()),
                'right': map(vr, self.cmd(f"get_property RIGHT [get_bd_pins -of {self.obj}]").split())
            }

            for i in [ dict(zip(attrs, t)) for t in zip(*attrs.values()) ]:
                create_pin(self, **i)
