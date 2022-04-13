from .piradip_build_base import *

from .type import svtype
from .sv import dump_node

def upper_map(l):
    return dict([ (i, i.upper()) for i in l ])

axi4mm_lite_ports = [ 'awaddr', 'awprot', 'awvalid', 'awready', 'wdata', 'wstrb', 'wvalid', 'wready',
                      'bresp', 'bvalid', 'bready', 'araddr', 'arprot', 'arvalid', 'arready',
                      'rdata', 'rresp', 'rvalid', 'rready' ]

axi4mm_ports = [ 'awid', 'awaddr', 'awlen', 'awsize', 'awburst',
                 'awlock', 'awcache', 'awprot', 'awregion', 'awqos', 'awuser',
                 'awvalid', 'awready', 'wdata', 'wstrb', 'wlast', 'wuser', 'wvalid',
                 'wready', 'bid', 'bresp', 'buser', 'bvalid', 'bready',
                 'arid', 'araddr', 'arlen', 'arsize', 'arburst', 'arlock',
                 'arcache', 'arprot', 'arregion', 'arqos', 'aruser',
                 'arvalid', 'arready', 'rid', 'rdata', 'rresp', 'rlast',
                 'ruser', 'rvalid', 'rready' ]

axi4s_ports = [ 'tdata', 'tstrb', 'tlast', 'tvalid', 'tready' ]


ipxact_map = {
    "axi4mm_lite": {
        "memoryMapped": True,
        "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm", 'version': "1.0" },
        "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm_rtl", 'version': "1.0" },
        "ports":  axi4mm_lite_ports,
        "port_map": upper_map(axi4mm_lite_ports),
        "clock": { 'name': "clk" },
        "reset": { 'name': "resetn", 'polarity': 'low' }
        },
    "axi4mm": {
        "memoryMapped": True,
        "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm", 'version': "1.0" },
        "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm_rtl", 'version': "1.0" },
        "ports":  axi4mm_ports,
        "port_map": upper_map(axi4mm_ports),
        "clock": { 'name': "clk" },
        "reset": { 'name': "resetn", 'polarity': 'low' }
        },    
    "axi4s": {
        "memoryMapped": False,
        "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "axis", 'version': "1.0" },
        "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "axis_rtl", 'version': "1.0" },
        "ports":  axi4s_ports,
        "port_map": upper_map(axi4s_ports),
        "clock": { 'name': "clk" },
        "reset": { 'name': "resetn", 'polarity': 'low' }
        }
    }

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



class Port:
    def parse_set(n, parent):
        v = []

        try:
            port_root = r.get(n,"kModuleHeader/kParenGroup/kPortDeclarationList")

            for port_node in port_root.children:
                if port_node.tag in [ '(', ',', ')' ]:
                    continue
                if port_node.tag != 'kPortDeclaration':
                    WARN(f"not handling tag {port_node.tag}")
                    continue

                p = Port.parse(port_node, parent)

                v.append(p)
                
        except anytree.resolver.ResolverError:
            WARN(f"Ports: no ports detected")

        return v

    def parse(n, parent):
        name = r.get(n, "kUnqualifiedId/SymbolIdentifier").text

        try:
            iface_node = r.get(n, 'kDataType/kInterfacePortHeader')

            iface_name = r.get(iface_node, 'kUnqualifiedId/SymbolIdentifier').text
            modport_name = r.get(iface_node, 'SymbolIdentifier').text
            
            return InterfacePort(name, parent, iface_name, modport_name)

        except anytree.resolver.ResolverError:
            name = r.get(n, "kUnqualifiedId/SymbolIdentifier").text
            
            direction = ""
            svt = None
            
            if n.children[0].tag == 'input':
                direction = 'input'
            elif n.children[0].tag == 'output':
                direction = 'output'
            else:
                ERROR(f"Unhandled direction: {n.children[0].tag}")

            try:
                svt = svtype.parse(r.get(n, "kDataType"))
            except Exception as e:
                print(e)
                dump_node(f"Error in getting type for port {name}", n)
                ERROR(f"{name}")
                
                
            return SimplePort(name, parent, direction, svt)
    
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.parent.ports[self.name] = self

    @property
    def is_clk(self):
        return False

    @property
    def is_rst(self):
        return False

        
class SimplePort(Port):
    def __init__(self, name, parent, direction, svtype):
        super(SimplePort, self).__init__(name, parent)
        self.direction = direction
        self.svtype = svtype

    def __repr__(self):
        return f"{self.direction} {self.svtype.typename} {self.name}"

    @property
    def param_decls(self):
        return []
    
    @property
    def params(self):
        return {}

    @property
    def ports(self):
        return {}

    @property
    def decl(self):
        return f"{self.direction} {self.svtype.typename} {self.name}"
    
    def get_wrapper_ports(self):
        return [ self.decl ]

    def get_port_assignments(self):
        return [ f".{self.name}({self.name})" ]

    def generate_body(self, f):
        pass

    def generate_ipxact(self, ipx):
        ipx.model.ports.add(self.name, self.direction, self.svtype)

class WrappedPort:
    def __init__(self, ifport, port):
        self.ifport = ifport
        self.port = port

        
    @property
    def name(self):
        return self.ifport.name + "_" + self.port.name
            
    @property
    def direction(self):
        return self.port.direction
    
    @property
    def svtype(self):
        t = self.port.svtype
        
        if self.port.svtype.basetype in self.ifport.types:
            assert self.port.svtype.packed_range == None, "Can't handle 2-D types yet"
            t = self.ifport.types[self.port.svtype.basetype]

        if not t.definite_range:
            t = svtype(t.basetype, (self.ifport.substitute_parameters(t.packed_range[0]), self.ifport.substitute_parameters(t.packed_range[1])), default_range=("0", "0"))
            
        return t

    @property
    def decl(self):
        return self.ifport.substitute_parameters(f"{self.direction} {self.svtype.typename} {self.name}")                

    @property
    def is_clk(self):
        return self.port.name == "aclk"

    @property
    def is_rst(self):
        return self.port.name == "aresetn"

    
class WrappedParameter:
    def __init__(self, ifport, param):
        self.ifport = ifport
        self.param = param

    def __str__(self):
        return "<|"+self.decl+"|>"

    @property
    def interface(self):
        return self.ifport.interface
    
    @property
    def pdesc(self):
        return self.interface.pdescs.get(self.param.name, {})

    @property
    def name(self):
        return self.ifport.name.upper() + "_" + self.param.name

    @property
    def description(self):
        return self.pdesc.get('description', self.name)

    @property
    def hidden(self):
        return self.pdesc.get('hidden', False)
        
    @property
    def typename(self):
        return self.param.typename

    @property
    def default(self):
        return self.ifport.substitute_parameters(self.param.default)

    @property
    def decl(self):
        v = f"parameter {self.typename} {self.name}"
        if self.param.default != "":
           v += f" = {self.default}"
        return v

    
class InterfacePort(Port):
    def __init__(self, name, parent, interface, modport):
        super(InterfacePort, self).__init__(name, parent)
        self.modport = interfaces[interface].modports[modport]

        self.port_map = { 'clk': 'aclk', 'resetn': 'aresetn' }
        self.rport_map = { v: k for k,v in self.port_map.items() }
        
        self.ports = { self.rport_map.get(p.name, p.name): WrappedPort(self, p) for p in self.modport.ports.values() }
        self.params = { p.name: WrappedParameter(self, p) for p in self.interface.params.values() }
        
        self.param_prefix = name.upper() + "_"
        self.prefix = name + "_"
        self.param_re = re.compile(r"(^|[^0-9A-Za-z_])(" + "|".join(self.modport.iface.params.keys()) + "|BYTE_WIDTH)([^0-9A-Za-z_]|$)")
        self.wrapper_params = {}

        for p in self.params.values():
            self.wrapper_params[p.name] = self.param_prefix + p.name

    @property
    def types(self):
        return self.interface.types

    @property
    def exposed_params(self):
        return filter(lambda p: not p.hidden, self.params.values())
    
    @property
    def interface(self):
        return self.modport.iface

    @property
    def param_decls(self):
        return [ p.decl for p in self.params.values() ]

    def substitute_parameters(self, s):
        return self.param_re.sub(r"\1"+self.param_prefix+r"\2\3", s)
    
    def port_type(self, n):
        self.modport.resolve_type(self.types[n])
        
    def get_wrapper_ports(self):
        v = []

        for i in self.ports.values():
            v += [ f"{i.direction} {i.svtype.typename} {self.prefix}{i.name}" ]
                
        v = [ self.param_re.sub(r"\1"+self.param_prefix+r"\2\3", i) for i in v ]
                
        return v
        
    def get_port_assignments(self):
        return [ f".{self.name}({self.name})" ]

    def generate_verilog(self, f):
        print(f"    {self.modport.iface.name} #(", file=f)
        print("        "+",\n        ".join([ f".{p.param.name}({p.name})" for p in self.params.values()]), file=f)
        print(f"    ) {self.name} (", file=f)

        print("        "+",\n        ".join([ f".{p.name}({self.ports[p.name].name})" for p in self.interface.ports.values() ]), file=f)
        
        print(f"    );", file=f)
        

    def generate_ipxact(self, ipx):
        ipxdesc = ipxact_map.get(self.interface.name, None)

        for num, p in enumerate(self.exposed_params):
            assert p.hidden == False
            ipx.model.model_parameters.add(p.name, "integer", p.name, p.name, p.default)
            ipx.parameters.add(p.name, p.default, displayName=p.name, description=p.description,
                               value_attr= { ipx.attr("format"): "long",
                                             ipx.attr("id"): f"PARAM_VALUE.{p.name}",
                                             ipx.attr("order"): f"{num}",
                                             ipx.attr("resolve"): "user"
                               })
        
        for p in self.ports.values():
            direction = p.direction
            
            if (p.is_clk or p.is_rst):
                direction = "input"

            ipx.model.ports.add(p.name, direction, svtype = p.svtype, views = [ "xilinx_anylanguagesynthesis", "xilinx_verilogbehavioralsimulation" ])

        if ipxdesc:
            INFO(f"Mapping {self.parent.name} port {self.name} (interface {self.interface.name}) to IP-XACT interface {ipxdesc['busType']['name']}")
            busname = self.name.upper()
            rst_busname = None
            bi = ipx.bus_interfaces.add(0, busname, ipxdesc)

            if ipxdesc.get('memoryMapped', False):
                if self.modport.name != 'SUBORDINATE':
                    ERROR(f"DON'T KNOW HOW TO HANDLE MASTERS YET: {self.interface.name}.{self.modport.name}")

                usage = "memory" if self.interface.name == "axi4mm" else "register"
                    
                mmap = ipx.memory_maps.add(bi.name, "4096", "32", usage)
                bi.make_slave(mmap)
            else:
                if self.modport.name == 'SUBORDINATE':
                    bi.make_slave()
                else:
                    bi.make_master()
                
            for n in ipxdesc["ports"]:
                bi.map_port(ipxdesc["port_map"][n], self.ports[n].name)

            rst_port = ipxdesc.get('reset', None)
            clk_port = ipxdesc.get('clock', None)
            rst_name = ""

            if rst_port:
                rst_name = self.ports[rst_port['name']].name
                rst_busname = f"{busname}_RST"
                bi = ipx.bus_interfaces.add(1, rst_busname, reset_busif_desc)

                bi.make_slave()

                bi.map_port("RST", rst_name)

                if rst_port['polarity'] == 'low':
                    bi.parameters.add("POLARITY", "ACTIVE_LOW", f"BUSIFPARAM_VALUE.{rst_busname}.POLARITY")
                elif rst_port['polarity'] == 'high':
                    bi.parameters.add("POLARITY", "ACTIVE_HIGH", f"BUSIFPARAM_VALUE.{rst_busname}.POLARITY")
                else:
                    ERROR(f"Unknown reset polarity '{rst_port['polarity']}")
                
            
            if clk_port:
                clk_busname = f"{self.name.upper()}_CLK"
                bi = ipx.bus_interfaces.add(1, clk_busname, clock_busif_desc)

                bi.make_slave()

                bi.map_port("CLK", self.ports[clk_port['name']].name)

                bi.parameters.add("ASSOCIATED_BUSIF", busname, f"BUSIFPARAM_VALUE.{clk_busname}.ASSOCIATED_BUSIF")
                if rst_busname:
                    bi.parameters.add("ASSOCIATED_RESET", rst_name, f"BUSIFPARAM_VALUE.{clk_busname}.ASSOCIATED_RESET")

        

class ModportPort(Port):
    def __init__(self, name, parent, direction):
        super(ModportPort, self).__init__(name, parent)
        self.direction = direction

    @property
    def svtype(self):
        return self.parent.iface.types[self.name]

    def generate_ipxact(self, ipx):
        print("MODPORT GENERATE IPX")
