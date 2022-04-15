from .piradip_build_base import *
from .structure import module_list
from .sv import parse, get_modules, dump_node
from .svbase import *
from .ipxact import IPXACTModule
from .port import svport

import io
import os
from pathlib import PurePath, Path

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


        
class ModuleBase:
    def __init__(self):
        pass
        
    @property
    def wrapper_path(self):
        return PurePath(self.desc['wrapper_name'])
    
    @property
    def wrapper_name(self):
        return self.desc['wrapper_name']

    @property
    def description(self):
        return self.desc['description']

    @property
    def display_name(self):
        return self.desc.get('display_name', self.name)
    
    @property
    def wrapper_verilog(self):
        return self.wrapper_path.joinpath('hdl').joinpath(self.desc.get('wrapper_file_name', f"{self.wrapper_name}_{self.version}.sv"))

    @property
    def rel_wrapper_verilog(self):
        return self.wrapper_path.joinpath('hdl').joinpath(self.desc.get('wrapper_file_name', f"{self.wrapper_name}_{self.version}.sv"))

    
    @property
    def wrapper_xml(self):
        return self.wrapper_path.joinpath(self.desc.get('xml_name', f"component.xml"))

    @property
    def rel_wrapper_xml(self):
        return self.desc.get('xml_name', f"component.xml")

    
    @property
    def bd_tcl(self):
        return self.wrapper_path.joinpath('bd/bd.tcl')

    @property
    def xgui_tcl(self):
        return self.wrapper_path.joinpath('xgui/xgui.tcl')
    
    @property
    def ipxact_name(self):
        return self.desc['wrapper_name']

    @property
    def version(self):
        return self.desc['version']

    

class svmodule(ModuleBase):
    def __init__(self, header, body):
        pass

        self.header = header
        self.body = body

        self.name = header.name
        modules[self.name] = self

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
        
    @property
    def desc(self):
        return module_list[self.name]

@svex("kModuleDeclaration")
def parse_svinterfacedecl(node):
    assert_nchild(node, 4)
    assert node.children[2].tag == 'endmodule'
    assert svexcreate(node.children[3]) == None  # Should just be instance

    return svmodule(svexcreate(node.children[0]), svexcreate(node.children[1]))

    
def build_modules():
    module_files = set([ v['file'] for _, v in module_list.items() ])
    module_names = set([ v for v in module_list ])
    
    for filename in module_files:
        root = parse(filename)

        module_nodes = get_modules(root)

        for n in module_nodes:
            name = r.get(n, "kModuleHeader/SymbolIdentifier").text

            if name in module_names:
                svexcreate(n)



    
class WrapperIfacePort:
    def __init__(self, module, port):
        self.module = module
        self.interface_port = port
        self.interface = port.interface
        self.modport = port.modport

        self.param_map = {}
        self.data_map = {}
        self.port_map = {}
        
        param_prefix = f"{port.name.upper()}_"
        port_prefix = f"{port.name}_"
        
        ns = { **{ p.name: svsymbol(param_prefix + p.name) for p in self.interface.params.values() }, **global_type_punts }
        
        for p in self.interface.params.values():
            pname = param_prefix + p.name

            self.param_map[pname] = p
            self.module.params[pname] = p.subst(ns)

        for p in self.interface.ports.values():
            pname = port_prefix + p.name

            self.port_map[pname] = p
            self.module.ports[pname] = p.subst(ns)

        for p in self.modport.ports.values():
            if p.name in [ "aclk", "aresetn" ]:
                continue
            
            pname = port_prefix + p.name

            data = self.interface.datas[p.name]
            
            self.data_map[pname] = p

            d = data.subst(ns)

            print(f"{p} {d}")

            self.module.ports[pname] = svport(p.direction, d.datatype, pname)
            
        print(self.param_map)
        print(self.port_map)
        print(self.data_map)
        print(ns)

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



    
class WrapperModule(ModuleBase):
    def __init__(self, module):
        self.name = module.wrapper_name
        self.module = module

        self.params = {}
        self.param_map = {}
        self.ports = {}
        self.interface_ports = { p.name: WrapperIfacePort(self, p) for p in filter(lambda x: x.is_interface_port, self.module.ports.values()) }
        
        for p in module.params.values():
            self.params[p.name] = p

        for p in module.ports.values():
            if not p.is_interface_port:
                self.ports[p.name] = p

    @property
    def has_interfaces(self):
        return len(self.interface_ports) > 0
                
    @property
    def desc(self):
        return self.module.desc

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

        print(8*" "+(",\n"+8*" ").join([f".{n}({n})" for n in self.params ]))

        print(f"    ) {self.module.name}_inst (", file=f)
        
        print(8*" "+(",\n"+8*" ").join([ f".{p.name}({p.name})" for p in self.module.ports.values() ]), file=f)
            
        print(f"    );", file=f);
            
        print("endmodule", file=f)

        


def wrap_modules():
    for m in modules.values():
        os.makedirs(m.wrapper_verilog.parent, exist_ok=True)
        
        INFO(f"Generating wrapper for {m.name} at {m.wrapper_verilog}")

        w = WrapperModule(m)
        
        f = open(m.wrapper_verilog, "w")

        w.generate_verilog(f)

        INFO(f"Generating IP-XACT for {m.name} at {m.wrapper_xml}...")
        os.makedirs(m.wrapper_xml.parent, exist_ok=True)

        f = open(m.wrapper_xml, "w")

        ipx = IPXACTModule(w)

        ipx.generate()

        ipx.export_ipxact(f)
        



