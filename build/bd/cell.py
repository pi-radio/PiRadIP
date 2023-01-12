from .obj import BDObj

class BDCell(BDObj):
    def __init__(self, parent, name):
        super().__init__(parent, name)
        if self.parent is not None:
            self.parent.cells[name] = self
        self.pins = dict()
        self.intf_pins = dict()
            
    @property
    def obj(self):
        return f"[get_bd_cell {self.path}]"
        
