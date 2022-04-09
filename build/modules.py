from .piradip_build_base import *
from .structure import module_list
from .sv import parse, get_modules, dump_node
from .ipxact import IPXACTModule

from .parameter import Parameter
from .port import Port

import io

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
    def module_desc(self):
        return module_list[self.name]
    
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
    def wrapper_file_name(self):
        return self.module_desc.get('wrapper_file_name', f"{self.wrapper_name}_{self.version}.v")
    
    @property
    def ipxact_name(self):
        return self.module_desc['wrapper_name']

    @property
    def version(self):
        return self.module_desc['version']
    
    def generate_wrapper(self, f):
        print("`timescale 1ns/1ps", file=f)
        print(f"module {self.wrapper_name} #(", file=f)

        param_list = []

        for p in self.ports.values():
            param_list += p.get_wrapper_params()

        for p in self.params.values():
            param_list += p.get_decl()
            
        print("    "+",\n    ".join(param_list), file=f)
        

        print(") (", file = f)

        port_list = []

        for p in self.ports.values():
            port_list += p.get_wrapper_ports()

        port_list = [ normalize_types(p) for p in port_list ]
            
        print("    "+",\n    ".join(port_list), file=f)
        
        print(");", file=f)

        for p in self.ports.values():
            p.generate_body(f)

        print(f"    {self.name} #(", file=f)
        print(f"    ) {self.name}_inst (", file=f);

        port_assignments = []
        
        for p in self.ports.values():
            port_assignments += p.get_port_assignments()

        print("    "+",\n    ".join(port_assignments), file=f)
            
        print(f"    );", file=f);
            
        print("endmodule", file=f)


    def generate_ipxact(self, f):
        ipx = IPXACTModule(self)

        for p in self.params.values():
            p.generate_ipxact(ipx)
        
        for p in self.ports.values():
            p.generate_ipxact(ipx)

        ipx.export_ipxact(f)
            

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
        print(f"Generating wrapper for {m.name}...")
        f = io.StringIO()

        m.generate_wrapper(f)
        
        print(f.getvalue())


    for _, m in modules.items():
        print(f"Generating IP-XACT for {m.name}...")
        f = io.StringIO()

        m.generate_ipxact(f)

        print(f.getvalue())
