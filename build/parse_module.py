#!/usr/bin/env python3

import sys

from verible_verilog_syntax import VeribleVerilogSyntax
import anytree
#import ipyxact.ipyxact as ipyxact

import structure
from interfaces import build_interfaces
from modules import build_modules, wrap_modules

r = anytree.Resolver("tag")


            
def wrap_interface(c, interface, port):
    port_name = r.get(port, "kUnqualifiedId/SymbolIdentifier").text
    interface_name = r.get(interface, "kUnqualifiedId/SymbolIdentifier").text
    modport_name = r.get(interface, "SymbolIdentifier").text

    c.add_interface(interface_name, modport_name, port_name)
    


def get_direction(port):
    d = port.find({ "tag": [ "input", "output", "inout" ] })

    return d.text
        
def wrap_module(module, wrapper_name=None):
    module_def = None
    
    header = module.find({ "tag": "kModuleHeader" })
    name = header.find({ "tag" : [ "SymbolIdentifier", "EscapedIdentifier" ]},
                       iter_=anytree.PreOrderIter).text

    try:
        module_def = export_modules[name]
    except:
        return

    c = Component(module_def)

    
    print(f"Wrapper name: {wrapper_name}")
        
    for port in header.iter_find_all({ "tag": [ "kPortDeclaration", "kPort" ]}):        
        data_type = r.get(port, "kDataType")

        print(dir(r))

        interface = None

        try:
            dump_node(data_type)
            interface = r.get(data_type, "kInterfacePortHeader")
        except:
            pass
    
        if (interface):
            wrap_interface(c, interface, port)
        else:
            port_name = r.get(port, "kUnqualifiedId/SymbolIdentifier").text
            dump_node(port)
            port_direction = get_direction(port)
        
            c.add_port(port_name, port_direction)

    c.export_wrapper_verilog()
    c.export_ipxact()



structure.add_interface("axi4mm", "library/aximm/piradip_aximm.sv")
structure.add_interface("axi4mm_lite", "library/aximm/piradip_axi4mmlite.sv")
structure.add_interface("axi4s", "library/axis/piradip_axis.sv")

structure.add_module("piradip_axis_sample_buffer_out",
                     "library/axis/piradip_axis_sample_buffer_out.sv",
                     wrapper_name="AXIS_SampleBufferOut",
                     description="A memory mapped sample buffer to stream out over an AXI stream interface",
                     display_name="AXI Sample Buffer Out")

build_interfaces()

build_modules()

wrap_modules()

#for module in ast.tree.iter_find_all({ "tag": "kModuleDeclaration" }):
#    wrap_module(module)

  
