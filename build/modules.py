from .piradip_build_base import *
from .structure import module_list
from .sv import parse, get_modules, dump_node
from .ipxact import IPXACTModule

from .parameter import Parameter
from .port import Port, InterfacePort

import io
import os
from pathlib import PurePath, Path

class WrapperModule:
    def __init__(self, module):
        self.name = module.wrapper_name
        self.module = module

        self.params = {}
        self.ports = {}

        self.interfaces = {}
        
        for p in module.params.values():
            self.params[p.name] = p

        for p in module.ports.values():
            if type(p) == InterfacePort:
                for port in p.ports.values():
                    self.ports[port.name] = port

                self.interfaces[p.name] = p

                for param in p.params.values():
                    self.params[param.name] = param
            else:
                self.ports[p.name] = p
                    

    def generate_verilog(self, f):
        print("`timescale 1ns/1ps", file=f)
        print(f"module {self.name} #(", file=f)
            
        print("    "+",\n    ".join([p.decl for p in self.params.values()]), file=f)

        print(") (", file = f)

        print("    "+",\n    ".join([normalize_types(p.decl) for p in self.ports.values()]), file=f)

        print(");", file=f)


        for i in self.interfaces.values():
            print("", file=f)

            i.generate_verilog(f)

            for p in filter(lambda p: not p.is_clk and not p.is_rst and p.direction == 'input', i.ports.values()):
                print(f"    assign {i.name}.{p.port.name} = {p.name};", file=f)
                
            for p in filter(lambda p: not p.is_clk and not p.is_rst and p.direction == 'output', i.ports.values()):
                print(f"    assign {p.name} = {i.name}.{p.port.name};", file=f)

        omit_list = [ "aclk", "aresetn" ]

        print("", file=f)
        
        print(f"    {self.module.name} #(", file=f)
        print(f"    ) {self.module.name}_inst (", file=f)
        
        port_assignments = []
        
        for p in self.module.ports.values():
            port_assignments += p.get_port_assignments()

        print(8*" "+(",\n"+8*" ").join([ f".{p.name}({p.name})" for p in self.module.ports.values() ]), file=f)
            
        print(f"    );", file=f);
            
        print("endmodule", file=f)

    def generate_ipxact(self, f):
        ipx = IPXACTModule(self)

        for p in self.module.params.values():
            pass # p.generate_ipxact(ipx)
        
        for p in self.module.ports.values():
            p.generate_ipxact(ipx)

        ipx.export_ipxact(f)

    @property
    def ipxact_name(self):
        return self.module.ipxact_name

    @property
    def version(self):
        return self.module.version

    @property
    def wrapper_path(self):
        return self.module.wrapper_path
    
    @property
    def wrapper_verilog(self):
        return self.module.wrapper_verilog

    @property
    def bd_tcl(self):
        return self.module.bd_tcl

    @property
    def xgui_tcl(self):
        return self.module.xgui_tcl
 
    @property
    def display_name(self):
        return self.module.display_name
        
class Module:
    def parse(n):
        name = r.get(n, "kModuleHeader/SymbolIdentifier").text

        module = Module(name)

        Parameter.parse_set(n, module)

        Port.parse_set(n, module)
        
    def __init__(self, name):
        self.name = name
        modules[self.name] = self
        self.params = {}
        self.ports = {}
        self.types = {}

    def __repr__(self):
        return f"module {self.name} #({self.param_list}) ({self.ports})"

    @property
    def wrapper(self):
        return WrapperModule(self)
    
    @property
    def module_desc(self):
        return module_list[self.name]

    @property
    def wrapper_path(self):
        return PurePath(self.module_desc['wrapper_name'])
    
    @property
    def wrapper_name(self):
        return self.module_desc['wrapper_name']

    @property
    def description(self):
        return self.module_desc['description']

    @property
    def display_name(self):
        return self.module_desc.get('display_name', self.name)
    
    @property
    def wrapper_verilog(self):
        return self.wrapper_path.joinpath('hdl').joinpath(self.module_desc.get('wrapper_file_name', f"{self.wrapper_name}_{self.version}.sv"))

    @property
    def wrapper_xml(self):
        return self.wrapper_path.joinpath(self.module_desc.get('xml_name', f"component.xml"))

    @property
    def bd_tcl(self):
        return self.wrapper_path.joinpath('bd/bd.tcl')

    @property
    def xgui_tcl(self):
        return self.wrapper_path.joinpath('xgui/xgui.tcl')
    
    @property
    def ipxact_name(self):
        return self.module_desc['wrapper_name']

    @property
    def version(self):
        return self.module_desc['version']

    def resolve(self):
        pass
            

logic_re = re.compile(r"([^0-9A-Za-z_])logic([^0-9A-Za-z_])")
        
def normalize_types(s):
    return logic_re.sub(r"\1wire\2", s)
        
def build_modules():
    module_files = set([ v['file'] for _, v in module_list.items() ])
    module_names = set([ v for v in module_list ])
    
    for filename in module_files:
        root = parse(filename)

        module_nodes = get_modules(root)

        for n in module_nodes:
            name = r.get(n, "kModuleHeader/SymbolIdentifier").text

            if name in module_names:
                Module.parse(n)

def wrap_modules():
    for m in modules.values():
        
        
        os.makedirs(m.wrapper_verilog.parent, exist_ok=True)
        
        INFO(f"Generating wrapper for {m.name} at {m.wrapper_verilog}")
        
        f = open(m.wrapper_verilog, "w")

        m.wrapper.generate_verilog(f)

        INFO(f"Generating IP-XACT for {m.name} at {m.wrapper_xml}...")
        os.makedirs(m.wrapper_xml.parent, exist_ok=True)

        f = open(m.wrapper_xml, "w")

        m.wrapper.generate_ipxact(f)


