from .piradip_build_base import *
from .structure import module_map
from .sv import parse, get_modules, dump_node
from .svbase import *
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
    'axi_resp_t': 'logic [1:0]',
    'axi_burst_t': 'logic [1:0]',
    'axi_size_t': 'logic [2:0]',
    'axi_len_t': "logic [7:0]",
    'axi_prot_t': 'logic [2:0]',
    'axi_cache_t': 'logic [3:0]',
    'axi_qos_t': 'logic [3:0]',
    'axi_region_t': 'logic [3:0]',
    'axi_lock_t': 'logic'
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

    


class WrappedParameter(svparameter):
    def __init__(self, parent, param):
        super(WrappedParameter, self).__init__(
            svparametertype(
                param.basetype,
                param.packed_dimensions,
                param.name,
                param.unpacked_dimensions
            ),
            param.default,
            param.local
        )

        self.parent = parent

    def subst(self, ns):
        return WrappedParameter(self.parent, super(WrappedParameter, self).subst(ns))
        
    @property
    def desc(self):
        return self.parent.desc.param_map.get(self.name, None)

    @property
    def allowed_values(self):
        if self.desc == None:
            return None
        
        return self.desc.allowed_values        
    
    
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
        
        param_prefix = f"{port.name.upper()}_"
        port_prefix = f"{port.name}_"
        
        ns = { **{ p.name: svsymbol(param_prefix + p.name) for p in self.interface.params.values() }, **global_type_punts }
        
        for p in self.interface.params.values():
            pname = param_prefix + p.name

            wp = WrappedParameter(self, p)
            
            self.param_map[pname] = wp
            self.module.params[pname] = wp.subst(ns)

        for p in self.interface.ports.values():
            pname = port_prefix + p.name

            if p.name == self.desc.ipxdesc.reset.name:
                self.reset = pname

            if p.name == self.desc.ipxdesc.clock.name:
                self.clock = pname
            
            self.port_map[pname] = p
            self.module.ports[pname] = p.subst(ns)

        for p in self.modport.ports.values():
            if p.name in [ "aclk", "aresetn" ]:
                continue
            
            pname = port_prefix + p.name

            data = self.interface.datas[p.name]
            
            self.data_map[pname] = p

            d = data.subst(ns)

            self.module.ports[pname] = svport(p.direction, d.datatype, pname)

        
    @property
    def ipxdesc(self):
        return self.interface.ipxdesc

    @property
    def busname(self):
        return self.interface_port.name.upper()
    
    @property
    def name(self):
        return f"{self.interface.name}_inst"

    def generate_verilog(self, f):
        print(f"    {self.interface.name} #(", file=f)
        print("        "+",\n        ".join([ f".{self.param_map[p].name}({p})" for p in self.param_map]), file=f)
        print(f"    ) {self.name} (", file=f)

        print("        "+",\n        ".join([ f".{self.port_map[p].name}({p})" for p in self.port_map ]), file=f)
        
        print(f"    );", file=f)

        for p in filter(lambda p: self.data_map[p].direction == 'input', self.data_map):
            print(f"    assign {self.name}.{self.data_map[p].name} = {p};", file=f)
            
        for p in filter(lambda p: self.data_map[p].direction == 'output', self.data_map):
            print(f"    assign {p} = {self.name}.{self.data_map[p].name};", file=f)

    
class WrapperModule:
    def __init__(self, module):
        self.desc = module_map[module.name]
        self.name = self.desc.wrapper_name
        self.module = module

        self.params = {}
        self.param_map = {}
        self.ports = {}
        self.interface_ports = { p.name: WrapperIfacePort(self, p) for p in filter(lambda x: x.is_interface_port, self.module.ports.values()) }
        
        for p in module.params.values():
            self.params[p.name] = WrappedParameter(self, p)

        for p in module.ports.values():
            if not p.is_interface_port:
                self.ports[p.name] = p

        if dump_definitions:
            print("Wrapper module definitions")
            print("================================")
            print("  Parameters:")
            
            for p in self.params:
                print(f"    {p}")
                
            print("  Ports:")

            for p in self.ports:
                print(f"    {p}")

    @property
    def has_interfaces(self):
        return len(self.interface_ports) > 0
                
    def generate_verilog(self, f):
        print("`timescale 1ns/1ps", file=f)
        print(f"module {self.name} #(", file=f)
            
        print("    "+",\n    ".join([p.decl for p in self.params.values()]), file=f)

        print(") (", file = f)

        print("    "+",\n    ".join([p.decl for p in self.ports.values()]), file=f)

        print(");", file=f)


        for i in self.interface_ports.values():
            print("", file=f)

            i.generate_verilog(f)

        omit_list = [ "aclk", "aresetn" ]

        print("", file=f)
        
        print(f"    {self.module.name} #(", file=f)

        print(8*" "+(",\n"+8*" ").join([f".{n}({n})" for n in self.params ]), file=f)

        print(f"    ) {self.module.name}_inst (", file=f)
        
        print(8*" "+(",\n"+8*" ").join([ f".{p.name}({p.name})" for p in self.module.ports.values() ]), file=f)
            
        print(f"    );", file=f);
            
        print("endmodule", file=f)

        


        



