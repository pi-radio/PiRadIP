from .obj import bdactive
from .pin import BDPin, BDIntfPin
from .cell import BDCell

class BDHier(BDCell):
    def __init__(self, parent, name):
        super().__init__(parent, name)
        parent.make_active()
        self.cmd(f"create_bd_cell -type hier \"{name}\"")
        self.n_conn = 0

    @bdactive
    def connect(self, c1, c2):
        if isinstance(c1, BDIntfPin):
            assert(isinstance(c2, BDIntfPin))
            net_name = f"conn_{c1.name}_{c2.name}" if c1.name != c2.name else f"conn_{c1.name}"
            self.cmd(f"connect_bd_intf_net -intf_net {net_name} {c1.obj} {c2.obj}")
        else:
            print(type(c1).__name__)
            print(type(c2).__name__)
            raise Exception("Unable to connect these objects")
