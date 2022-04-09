from .piradip_build_base import *

class Port:
    def parse_set(n, parent):
        v = []

        try:
            port_root = r.get(n,"kModuleHeader/kParenGroup/kPortDeclarationList")

            for port_node in port_root.children:
                if port_node.tag in [ '(', ',', ')' ]:
                    continue
                if port_node.tag != 'kPortDeclaration':
                    print(f"WARNING: not handling tag {port_node.tag}")
                    continue

                p = Port.parse(port_node, parent)

                v.append(p)
                
        except anytree.resolver.ResolverError:
            print(f"Ports: no ports detected")

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
            
            if n.children[0].tag == 'input':
                direction = 'input'
            elif n.children[0].tag == 'output':
                direction = 'output'
            else:
                error(f"Unhandled direction: {n.children[0].tag}")
                
            return SimplePort(name, parent, direction, r.get(n, "kDataType").text)
    
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.parent.ports[self.name] = self

class SimplePort(Port):
    def __init__(self, name, parent, direction, typename):
        super(SimplePort, self).__init__(name, parent)
        self.direction = direction
        self.typename = typename

    def __repr__(self):
        return f"{self.direction} {self.typename} {self.name}"

    def get_wrapper_params(self):
        return []
        
    def get_wrapper_ports(self):
        return [ f"{self.direction} {self.typename} {self.name}" ]

    def get_port_assignments(self):
        return [ f".{self.name}({self.name})" ]

    def generate_body(self, f):
        pass

    def generate_ipxact(self, ipx):
        ipx.add_port(self.name, self.direction, self.typename)
        print("Generate ipx")

class InterfacePort(Port):
    def __init__(self, name, parent, interface, modport):
        super(InterfacePort, self).__init__(name, parent)
        self.interface = interfaces[interface]
        self.modport = self.interface.modports[modport]
        self.param_prefix = name.upper() + "_"
        self.prefix = name + "_"
        self.param_re = re.compile(r"([^0-9A-Za-z_])(" + "|".join(self.modport.iface.params.keys()) + "|BYTE_WIDTH)([^0-9A-Za-z_])")

    @property
    def ports(self):
        return self.modport.ports

    @property
    def wrapped_ports(self):
        [ f"{self.prefix}{i}" for i in self.ports ]
        
    def get_wrapper_params(self):
        v = []

        for p in self.modport.iface.params.values():
            v.append(p.get_decl(self.param_prefix))
            
        return v
    
    def port_type(self, n):
        self.modport.resolve_type(self.types[n])
        
    def get_wrapper_ports(self):
        v = []

        for i in self.ports.values():
            v += [ f"{i.direction} {i.typename} {self.prefix}{i.name}" ]
                
        v = [ self.param_re.sub(r"\1"+self.param_prefix+r"\2\3", i) for i in v ]
                
        return v
        
    def get_port_assignments(self):
        return [ f".{self.name}({self.name})" ]
    
    def generate_body(self, f):
        port_map = { 'clk': 'aclk', 'resetn': 'aresetn' }
        
        print(f"    {self.modport.iface.name} #(", file=f)
        
        v = []
        
        for p in self.modport.iface.params.values():
            v.append("        "+p.get_propagate(self.param_prefix))
            
        print(",\n".join(v), file=f)
            
        print(f"    ) {self.name} (", file=f)
        
        v = []
        for p in self.modport.iface.ports.values():
            v.append(f"        .{p.name}({self.name}_{port_map.get(p.name, p.name)})")
            
        print(",\n".join(v), file=f)
        
        print(f"    );", file=f)

        omit_list = [ "aclk", "aresetn" ]
        
        print(file=f)
        
        for i in self.ports.values():
            if i.name not in omit_list and i.direction == 'input':
                print(f"    assign {self.name}.{i.name} = {self.name}_{i.name};", file=f)
                
        print(file=f)
                
        for i in self.ports.values():
            if i.name not in omit_list and i.direction == 'output':
                print(f"    assign {self.name}_{i.name} = {self.name}.{i.name};", file=f)

        print(file=f)


    def generate_ipxact(self, ipx):
        print("Generate ipx")


class ModportPort(Port):
    def __init__(self, name, parent, direction):
        super(ModportPort, self).__init__(name, parent)
        self.direction = direction
        self.data = parent.iface.datas[name]

    @property
    def typename(self):
        return self.data

    def generate_ipx(self, ipx):
        print("MODPORT GENERATE IPX")
