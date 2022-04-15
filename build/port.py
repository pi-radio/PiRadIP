from .piradip_build_base import *

from .expr import svexcreate, svinterfaceportheader
from .svbase import *

clock_busif_desc = {
    "memoryMapped": False,
    "busType": { 'vendor': "xilinx.com", 'library': "signal", 'name': "clock", 'version': "1.0" },
    "abstractionType":  { 'vendor': "xilinx.com", 'library': "signal", 'name': "clock_rtl", 'version': "1.0" },
    "ports":  [ "CLK" ],
    "port_map": { "clk": "CLK" }
};

reset_busif_desc = {
    "memoryMapped": False,
    "busType": { 'vendor': "xilinx.com", 'library': "signal", 'name': "reset", 'version': "1.0" },
    "abstractionType":  { 'vendor': "xilinx.com", 'library': "signal", 'name': "reset_rtl", 'version': "1.0" },
    "ports":  [ "RST" ],
    "port_map": { "reset": "RST" }
};



class svport:
    def __init__(self, direction, datatype, name):
        assert(datatype is not None)
        self.direction = direction
        self.datatype = datatype
        self.name = name

    def __repr__(self):
        return f"{self.direction} {self.datatype} {self.name}"

    def subst(self, ns):
        return svport(self.direction, subst(self.datatype, ns), subst(self.name, ns))
    
    @property
    def decl(self):
        return str(self.datatype)

    @property
    def is_interface_port(self):
        return self.datatype.is_interface_port

    @property
    def interface(self):
        assert self.is_interface_port
        return self.datatype.basetype.interface

    @property
    def modport(self):
        assert self.is_interface_port
        return self.datatype.basetype.modport
    
        
@svex("kInterfacePortHeader")
def parse_interface_port_header(node):
    assert_nchild(node, 3)
    assert node.children[1].tag == '.'
    return svinterfaceportheader(svexcreate(node.children[0]), svexcreate(node.children[2]))
        

@svex("kPortDeclaration")
def parse_port_declaration(node):
    assert_nchild(node, 6)
    direction = svexcreate(node.children[0])
    comb = svexcreate(node.children[1])
    datatype = svexcreate(node.children[2])
    portname = svexcreate(node.children[3])
    assert svexcreate(node.children[4]) == None, "Can't handle unpacked dimensions yet"
    assert svexcreate(node.children[5]) == None

    if datatype is None:
        datatype = svlogic()
    
    return svport(direction, datatype, portname)


svlistnode("kPortDeclarationList", [ "kPortDeclaration" ])

        
