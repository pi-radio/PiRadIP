from .cell import BDCell
from .connector import BDConnector
            
class BDHier(BDConnector, BDCell):
    hier = True
    
    def __init__(self, parent, name):
        super().__init__(parent, name)
        parent.make_active()
        self.cmd(f"create_bd_cell -type hier \"{name}\"")
        parent.cells[self.name]=self
        
