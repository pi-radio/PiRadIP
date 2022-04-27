from .piradip_build_base import *
from .structure import module_map
from .sv import parse, get_modules, dump_node
from .svbase import *
from .expr import svlogicvector
from .ipxact import IPXACTModule
from .port import svport

import io
import os
from pathlib import PurePath, Path

from .ipx import IPXScript
from .parameter import svparameter, svparametertype

#
# TODO: Parse the package
#
global_type_punts = {
    'axi_resp_t': svlogicvector(1, 0),
    'axi_burst_t': svlogicvector(1, 0),
    'axi_size_t': svlogicvector(2, 0),
    'axi_len_t': svlogicvector(7, 0),
    'axi_prot_t': svlogicvector(2, 0),
    'axi_cache_t': svlogicvector(3, 0),
    'axi_qos_t': svlogicvector(3, 0),
    'axi_region_t': svlogicvector(3, 0),
    'axi_lock_t': svlogic()
}

class svmodule:
    def __init__(self, header, body):
        self.header = header
        self.body = body

        self.name = header.name
        registered_modules[self.name] = self
        
        self.params = header.parameters
        self.ports = header.ports
        self.types = {}

        for i in body.types:
            self.types[i.typename] = i

        self.interfaces = { p.interface.name : p.interface for p in filter(lambda x: x.is_interface_port, self.ports.values()) }

        
    @property
    def wrapper(self):
        return WrapperModule(self)
    
    def __repr__(self):
        return f"module {self.name} #({self.param_list}) ({self.ports})"

@svex("kModuleDeclaration")
def parse_svinterfacedecl(node):
    assert_nchild(node, 4)
    assert node.children[2].tag == 'endmodule'
    assert svexcreate(node.children[3]) == None  # Should just be instance

    return svmodule(svexcreate(node.children[0]), svexcreate(node.children[1]))

def unresolved_symbols(ns):
    unresolved = set()

    for sym in ns.values():
        unresolved |= sym.unresolved

    return unresolved

def resolve_types(ns):
    known_symbols = set(ns.keys())

    while unresolved_symbols(ns) & known_symbols != set():    
        for n in ns:
            if not ns[n].const:
                ns[n] = subst(ns[n], ns)

    return ns

                
class WrappedParameter(svparameter):
    def __init__(self, parent, new_name, param, desc):
        super(WrappedParameter, self).__init__(
            svparametertype(
                param.basetype,
                param.packed_dimensions,
                new_name,
                param.unpacked_dimensions
            ),
            param.default,
            param.local
        )

        self.orig_param = param
        self.desc = desc
        self.parent = parent

    def __repr__(self):
        return f"WRAPPED({'local' if self.local else ''}{self.basetype}{self.packed_dimensions if self.packed_dimensions is not None else ''} {self.name} {self.unpacked_dimensions if self.unpacked_dimensions is not None else ''} = {self.default})"
        
    def subst(self, ns):
        return WrappedParameter(self.parent, self.name, super(WrappedParameter, self).subst(ns), self.desc)

    @property
    def propagator(self):
        return f".{self.orig_param.name}({self.name})"
    
    @property
    def allowed_values(self):
        if self.desc is not None:
            return self.desc.allowed_values
        return list()

class WrappedPort(svport):
    def __init__(self, parent, new_name, port):
        super(WrappedPort, self).__init__(port.direction, port.datatype, new_name)
        self.parent = parent
        self.orig_port = port

    def subst(self, ns):
        return WrappedPort(self.parent, self.name, self.orig_port.subst(ns))

    @property
    def propagator(self):
        return f".{self.orig_port.name}({self.name})"    
    
class WrapperIfacePort:
    def __init__(self, module, port):
        self.module = module
        self.interface_port = port
        self.interface = port.interface
        self.modport = port.modport
        self.desc = self.interface.desc

        
        self.param_map = {}
        self.data_map = {}
        self.port_map = {}

        self.clock = None
        self.reset = None
        
        self.param_prefix = f"{port.name.upper()}_"
        self.port_prefix = f"{port.name}_"

        ns = { **global_type_punts }

        for p in self.interface.params.values():
            ns[p.name] = svsymbol(self.wrap_param_name(p.name))
        
        local_update = { svsymbol(self.param_prefix + p.name): p.default.subst(ns) for p in self.interface.local_params.values() } 
        
        for p in self.interface.params.values():
            pname = self.wrap_param_name(p.name)

            pdesc = self.interface.desc.param_map.get(p.name, None)
            
            wp = WrappedParameter(self, pname, p, pdesc)
            
            self.param_map[pname] = wp

            if not p.local:
                self.module.outer_params[pname] = wp.subst(ns)

        typemap = {}
            
        for t in self.interface.types.values():
            typemap[t.typename] =  subst(t.datatype, ns)
            
        typemap = resolve_types(typemap)

        ns = { **ns, **typemap }
            
        for p in self.interface.ports.values():
            pname = self.wrap_port_name(p.name)

            if p.name == self.desc.ipxdesc.reset.name:
                self.reset = pname

            if p.name == self.desc.ipxdesc.clock.name:
                self.clock = pname

            wp = WrappedPort(self, pname, p)
                
            self.port_map[pname] = wp
            self.module.outer_ports[pname] = wp.subst(ns).subst(local_update)

        for p in self.modport.ports.values():
            if p.name in [ "aclk", "aresetn" ]:
                continue
            
            pname = self.wrap_port_name(p.name)

            data = self.interface.datas[p.name]
            
            self.data_map[pname] = p

            d = data.subst(ns)
            d = d.subst(local_update)

            self.module.outer_ports[pname] = svport(p.direction, d.datatype, pname)

    def wrap_param_name(self, name):
        desc = self.interface.desc.param_map.get(name, None)

        pname = ""
        
        if desc is not None:
            pname += desc.prefix

        pname += self.param_prefix

        return svsymbol(pname + name)

    def wrap_port_name(self, name):
        return svsymbol(self.port_prefix + name)

    
    @property
    def ipxdesc(self):
        return self.interface.ipxdesc

    @property
    def busname(self):
        return self.interface_port.name.upper()
    
    @property
    def name(self):
        return f"{self.interface_port.name}_if"

    @property
    def local_params(self):
        return filter(lambda p: self.param_map[p].local, self.param_map)
    
    @property
    def exposed_params(self):
        return filter(lambda p: not self.param_map[p].local, self.param_map)
    
    def generate_verilog(self, f):
        print(f"    {self.interface.name} #(", file=f)
        print("        "+",\n        ".join([ self.param_map[p].propagator for p in self.exposed_params]), file=f)
        print(f"    ) {self.name} (", file=f)

        print("        "+",\n        ".join([ p.propagator for p in self.port_map.values() ]), file=f)
        
        print(f"    );", file=f)

        for p in filter(lambda p: self.data_map[p].direction == 'input', self.data_map):
            print(f"    assign {self.name}.{self.data_map[p].name} = {p};", file=f)
            
        for p in filter(lambda p: self.data_map[p].direction == 'output', self.data_map):
            print(f"    assign {p} = {self.name}.{self.data_map[p].name};", file=f)


    @property
    def propagator(self):
        return f".{self.interface_port.name}({self.name}.{self.modport.name})"
    
class WrapperModule:
    def __init__(self, module):
        self.desc = module_map[module.name]
        self.name = self.desc.wrapper_name
        self.module = module

        self.outer_params = {}
        
        self.outer_ports = {}
        self.inner_ports = {}

        self.interface_ports = { p.name: WrapperIfacePort(self, p) for p in filter(lambda x: x.is_interface_port, self.module.ports.values()) }
        self.module_params = {}

        for p in self.module.ports.values():
            if p.is_interface_port:
                wp = WrapperIfacePort(self, p)
                self.interface_ports[p.name] = wp
                self.inner_ports[p.name] = wp
        
        for p in module.params.values():
            wp = WrappedParameter(self, p.name, p, self.desc.param_map.get(p.name, None))
            self.module_params[p.name] = wp
            self.outer_params[p.name] = wp

        local_update = { p: self.outer_params[p].default for p in self.local_params }

        for p in self.outer_params:
            self.outer_params[p] = subst(self.outer_params[p], local_update)
                    
        for p in module.ports.values():
            if not p.is_interface_port:
                wp = WrappedPort(self, p.name, p)
                self.outer_ports[p.name] = subst(wp, local_update)
                self.inner_ports[p.name] = subst(wp, local_update)

            
        if dump_definitions:
            print("Wrapper module definitions")
            print("================================")
            print("  Parameters:")
            
            for p in self.outer_params:
                print(f"    {p}")
                
            print("  Ports:")

            for p in self.outer_ports:
                print(f"    {p}")
        
    @property
    def has_interfaces(self):
        return len(self.interface_ports) > 0

    @property
    def exposed_params(self):
        return filter(lambda p: not self.outer_params[p].local, self.outer_params)

    @property
    def local_params(self):
        return filter(lambda p: self.outer_params[p].local, self.outer_params)
    
    def generate_verilog(self, f):
        print("`timescale 1ns/1ps", file=f)
        print(f"module {self.name} #(", file=f)
            
        print("    "+",\n    ".join([self.outer_params[p].decl for p in self.exposed_params]), file=f)

        print(") (", file = f)
        
        print("    "+",\n    ".join([p.decl for p in self.outer_ports.values()]), file=f)

        print(");", file=f)


        for i in self.interface_ports.values():
            print("", file=f)

            i.generate_verilog(f)

        omit_list = [ "aclk", "aresetn" ]

        print("", file=f)
        
        print(f"    {self.module.name} ", file=f, end='')

        if len(self.module_params):
            print(f" #(", file=f)
            print(8*" "+(",\n"+8*" ").join([ p.propagator for p in self.module_params.values() ]), file=f)
            print(f"      ) ", file=f, end='')

        print(f"{self.module.name}_inst (", file=f)
        
        print(8*" "+(",\n"+8*" ").join([ self.inner_ports[p].propagator for p in self.module.ports ]), file=f)
            
        print(f"    );", file=f);
            
        print("endmodule", file=f)

        


        



