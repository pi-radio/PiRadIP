from .port import create_port, BDPortBase
from .xilinx import IOBUF
import os.path

class TristatePin:
    def __init__(self, i, o, t, name=None, parent=None):
        if parent is None and i.parent == o.parent and o.parent == t.parent:
            parent = i.parent

        assert parent is not None
            
        if name is None:
            name = os.path.commonprefix([i.name, o.name, t.name])
            while name[-1] == "_":
                name = name[:-1]
                
        assert name is not None

        self.parent = parent
        self.name = name
        self.i = i
        self.o = o
        self.t = t
        
    def create_port(self, parent, name):
        return TristatePort(parent, name, self)

alist = [('BD', 41, 1306)]
    
class TristatePort(BDPortBase):
    virtual = True
    
    def __init__(self, parent, name, pin):
        super().__init__(parent, name)
        self.pin = pin
        
        assert self.parent.root

        iobuf = IOBUF(parent, self.name + "_iobuf")

        pin.i.connect(iobuf.pins["IOBUF_IO_O"], accept=alist)
        pin.o.connect(iobuf.pins["IOBUF_IO_I"], accept=alist)
        pin.t.connect(iobuf.pins["IOBUF_IO_T"], accept=alist)

        self.io_pin = iobuf.pins["IOBUF_IO_IO"]

        self.io = create_port(parent, self.name + "_io", direction="IO", pin_type="undef")

        self.io.create()
        
        parent.connect(self.io_pin, self.io)

    @property
    def obj(self):
        return self.io.obj

    def set_phys(self, ball, iostd="LVCMOS18"):
        self.parent.port_phys[self.io_pin.name] = (ball, iostd)
