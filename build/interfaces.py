from .piradip_build_base import *
from .structure import interface_map
from .sv import *



def resolve_type(name):
    return global_type_punts.get(name, name)

class svmodportitem:
    def __init__(self, name, ports):
        self.name = name
        self.ports = ports

class svmodportport:
    def __init__(self, direction, name):
        self.direction = direction
        self.name = name

    def __str__(self):
        return f"{self.direction} {self.name}"

    def __repr__(self):
        return f"{self.direction} {self.name}"
        
class svmodport:
    def __init__(self, name, ports):
        ports = ports.flatten()
        
        self.name = name
        self.ports = {}

        direction = "UNKNOWN"
        
        for n in ports:
            if n in [ "output", "input" ]:
                direction = n
            else:
                self.ports[n] = svmodportport(direction, n)

    def __str__(self):
        return f"modport {self.name} (" + ", ".join([f"{port.direction} {port.name}" for port in self.ports.values()]) + ");"

    def __repr__(self):
        return f"modport {self.name} (" + ", ".join([f"{port.direction} {port.name}" for port in self.ports.values()]) + ");"

    
class svmoduleheader:
    def __init__(self, mtype, name, parameters, ports):
        self.mtype = mtype
        self.name = name
        self.parameters = {}
        self.ports = {}

        if parameters is not None:
            for p in parameters:
                self.parameters[p.name] = p

        if ports is not None:
            for p in ports:
                self.ports[p.name] = p

class svdata:
    def __init__(self, datatype, name):
        self.datatype = datatype
        self.name = name

    def __repr__(self):
        return f"{self.datatype} {self.name}"

    @property
    def decl(self):
        return f"{self.datatype} {self.name}"
    
    def subst(self, ns):
        return svdata(subst(self.datatype, ns), subst(self.name, ns))
                
class svmodulebody(svflatlist):
    @property
    def parameters(self):
        return filter(lambda x: isinstance(x, svparameter), self.l)

    @property
    def modports(self):
        return filter(lambda x: isinstance(x, svmodport), self.l)

    @property
    def instantiations(self):
        return filter(lambda x: isinstance(x, svinstantiation), self.l)

    @property
    def types(self):
        return filter(lambda x: isinstance(x, svtypedecl), self.l)
    
    @property
    def datas(self):
        r = []
        
        for i in self.instantiations:
            for j in i.names:
                r.append(svdata(i.type, j.name))

        return r
    
class svinterface:
    def __init__(self, header, body):
        self.header = header
        self.body = body

        self.name = header.name
        self.desc = interface_map.get(self.name, {})
        registered_interfaces[self.name] = self

        self.params = header.parameters
        self.ports = header.ports
        self.types = {}
        self.modports = { }
        self.datas = {}

        ## TODO -- Get extra parameters from body
        for i in body.parameters:
            self.params[i.name] = i
        
        for i in body.types:
            self.types[i.typename] = i
        
        for i in body.modports:
            self.modports[i.name] = i

        for i in body.datas:
            self.datas[i.name] = i
        
    @property
    def ipxdesc(self):
        return self.desc.ipxdesc
        
    @property
    def pdescs(self):
        return self.desc.parameters
        
    def resolve_type(self, name):
        return resolve_type(self.types.get(name, name))

@svex("kModuleHeader")
def parse_module_header(node):
    assert_nchild(node, 8)
    mtype = node.children[0].tag
    assert svexcreate(node.children[1]) == None
    name = svexcreate(node.children[2])
    assert svexcreate(node.children[3]) == None
    parameters = svexcreate(node.children[4])
    ports = svexcreate(node.children[5])
    assert svexcreate(node.children[6]) == None
    assert node.children[7].tag == ';'

    return svmoduleheader(mtype, name, parameters, ports)

@svex("kModportSimplePort")
def parse_simple_port(node):
    assert_nchild(node, 2)
    assert svexcreate(node.children[1]) == None
    return svexcreate(node.children[0])

svpassnode("kModportSimplePort")

svlistnode('kModportSimplePortsDeclaration', [ 'output', 'input', 'kModportSimplePort' ])
    
svlistnode('kModportPortList', [ 'kModportSimplePortsDeclaration' ])

@svex("kModportItem")
def parse_modport_item(node):
    assert_nchild(node, 2)
    name = svexcreate(node.children[0])
    ports = svexcreate(node.children[1])
    return svmodport(name, ports)
    
svlistnode('kModportItemList', [ 'kModportItem' ])
    
@svex("kModportDeclaration")
def parse_modport_decl(node):
    assert_nchild(node, 3)
    assert node.children[0].tag == 'modport'
    assert node.children[2].tag == ';'
    return svexcreate(node.children[1])
    

    
svlistnode('kModuleItemList', module_item_list, svmodulebody)


    
    
@svex("kInterfaceDeclaration")
def parse_svinterfacedecl(node):
    assert_nchild(node, 4)
    assert node.children[2].tag == 'endinterface'
    assert svexcreate(node.children[3]) == None  # Should just be instance

    return svinterface(svexcreate(node.children[0]), svexcreate(node.children[1]))

