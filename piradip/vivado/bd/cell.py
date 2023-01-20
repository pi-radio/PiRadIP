from .obj import BDObj

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
    
