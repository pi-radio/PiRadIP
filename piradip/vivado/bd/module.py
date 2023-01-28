from .cell import BDCell


class BDModule(BDCell):
    def __init__(self, parent, name, src_mod):
        super().__init__(parent, name)
        self.src_mod = src_mod

        self.create()

    def create(self):
        self.cmd(f"create_bd_cell -type module -reference {self.src_mod} {self.name}")

        self.enumerate_pins()
