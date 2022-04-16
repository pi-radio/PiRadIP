from .piradip_build_base import *

from .structure import piradlib_files

from .ipxact_base import *
"""
from .ipxact_node import *
from .ipxact_bus import *
from .ipxact_collection import *
"""
from .ipxact_component import *
from .xilinx import *
from .sv import *

import io
import datetime
import os
import time

def stringize(s):
    return '"'+s+'"'

vendor = "pi-rad.io"
library = "piradip"
version = "1.0"


class TCLVar:
    def __init__(self, script, var):
        self.var = var
        self.s = script

    def set_prop(self, prop, val):
        self.s.cmd(f"::set_property {prop} {{{val}}} ${self.var};")

class TCLScript:
    def __init__(self):
        self._tcl_body = io.StringIO()

    def cmd(self, v):
        self._tcl_body.write(f"{v}\n")

    @property
    def body(self):
        return self._tcl_body.getvalue()
        
    def get_var(self, v):
        return TCLVar(self, v)

    def set_var(self, var, value):
        self.cmd(f"set {var} {value};\n")
        return TCLVar(self, var)

    def comment(self, c):
        self.cmd(f"# {c}")
    
        
class IPXScript(TCLScript):
    def __init__(self, module):
        super(IPXScript, self).__init__()
        self.module = module
        self.desc = module.desc
        self.n = 0
        self.param_ids = {}
        self.model_param_ids = {}
        self.model_param_refs = {}
        self.default_dict = {}

        self.xgui = TCLScript()
        
        
    def generate(self):
        self.comment("Create component")
        self.cmd(f"cd \"{self.desc.wrapper_path}\"\n")
        self.cmd(f"ipx::create_core {vendor} {library} {self.desc.wrapper_name} {self.desc.version}\n")

        self.xgui.cmd("proc init_gui { IPINST } {")
        self.xgui.cmd(" ipgui::add_param $IPINST -name \"Component_Name\"")
        self.xgui.cmd(" ipgui::add_page $IPINST -name \"Page 0\"")
        self.xgui.cmd("}")
        

        for p in self.module.params.values():
            self.param_ids[p.name] = svsymbol(f"PARAM_VALUE.{p.name}")
            self.model_param_ids[p.name] = svsymbol(f"MODELPARAM_VALUE.{p.name}")
            
            self.model_param_refs[p.name] = svsymbol(f"spirit:decode(id('{self.model_param_ids[p.name]}'))")
            self.default_dict[p.name] = p.default

        known_symbols = set(self.default_dict.keys())
            
        while not all([ x.const for x in self.default_dict.values()]):
            unresolved = set()
            
            for p in self.default_dict:
                unresolved |= self.default_dict[p].unresolved

            if (unresolved - known_symbols) != set():
                ERROR("Unhandled symbols: {unresolved - known_symbols}")
                
            for p in self.default_dict:
                if not self.default_dict[p].const:
                    self.default_dict[p] = subst(self.default_dict[p], self.default_dict)
        
        top = self.set_var("top", "[ipx::current_core]")

        self.comment("Define globals")
        
        top.set_prop("vendor", vendor)
        top.set_prop("library", library)
        
        top.set_prop("version", self.desc.version)
        top.set_prop("vlnv", f"{vendor}:{library}:{self.desc.ipxact_name}:{self.desc.version}")
        top.set_prop("core_revision", int(time.time()))
        top.set_prop("description", self.desc.description)
        top.set_prop("display_name", self.desc.display_name)
        top.set_prop("xilinx_version", "2021.2")
        top.set_prop("supports_vivado", "true")
        top.set_prop("hide_in_gui", "false")
        top.set_prop("taxonomy", "AXI_Peripheral")
        top.set_prop("supported_families", "zynquplus Pre-Production")
        #top.set_prop("tags", "{ }")

        self.comment("Generate parameters")
        
        for n, p in enumerate(sorted(self.module.params)):
            self.generate_parameter(n, self.module.params[p])

        self.comment("Generate ports")
            
        for n, p in enumerate(sorted(self.module.ports)):
            self.generate_port(n, p)

        self.comment("Generate interfaces")
            
        if self.module.has_interfaces:
            for i in self.module.interface_ports.values():
                if i.desc.ipxdesc is not None:
                    self.generate_interface(i)

        self.comment("Add file groups")
                    
        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_verilogsynthesis $top]")
        cfg.set_prop("display_name", "Verilog Synthesis")
        cfg.set_prop("language", "verilog")
        cfg.set_prop("model_name", self.module.name)
        cfg.set_prop("env_ids", "verilogSource:vivado.xilinx.com:synthesis")

        cf = self.set_var("current_file", f"[::ipx::add_file {self.desc.wrapper_verilog_relpath} $current_file_group]")
        cf.set_prop("type", "verilogSource")
        cf.set_prop("processing_order", "normal")
        
        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_verilogsimulation $top]")
        cfg.set_prop("display_name", "Verilog Simulation")
        cfg.set_prop("language", "verilog")
        cfg.set_prop("model_name", self.module.name)
        cfg.set_prop("env_ids", "verilogSource:vivado.xilinx.com:simulation")

        cf = self.set_var("current_file", f"[::ipx::add_file {self.desc.wrapper_verilog_relpath} $current_file_group]")
        cf.set_prop("type", "verilogSource")
        cf.set_prop("processing_order", "normal")

        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_xpgui $top]")
        cfg.set_prop("display_name", "UI Layout")
        cfg.set_prop("env_ids", ":vivado.xilinx.com:xgui.ui")

        cf = self.set_var(f"current_file", "[::ipx::add_file {self.module.desc.wrapper_xgui_relpath} $current_file_group]")
        cf.set_prop("type", "tclSource")
        cf.set_prop("processing_order", "normal")
        cf.set_prop("xgui_version", "2")

        cfg = self.set_var("current_file_group", "[::ipx::add_file_group bd_tcl $top]")
        cfg.set_prop("display_name", "Block Diagram")
        cfg.set_prop("env_ids", ":vivado.xilinx.com:block.diagram")
        
        cf = self.set_var("current_file", "[::ipx::add_file bd/bd.tcl $current_file_group]")
        cf.set_prop("type", "tclSource")
        cf.set_prop("processing_order", "normal")
                    
        self.cmd("ipx::create_bd_file [ipx::current_core]")

        self.cmd("ipx::save_core")
        
        
    def generate_parameter(self, n, p):
        self.comment(f"Parameter {p.name}")
        
        cup = self.set_var("current_user_parameter", f"[::ipx::add_user_parameter {p.name} $top]")

        cup.set_prop("description", p.name)
        cup.set_prop("display_name", p.name)
        cup.set_prop("enablement_value", "true")
        cup.set_prop("ipxact_id", f"PARAM_VALUE.{p.name}")
        cup.set_prop("usage", "all")
        cup.set_prop("order", n)
        cup.set_prop("value", p.default)
        cup.set_prop("value_format", "long")
        cup.set_prop("value_resolve_type", "user")
        cup.set_prop("value_source", "default")

        if p.allowed_values is not None:
            cup.set_prop("value_validation_list", "32")
            cup.set_prop("value_validation_pairs", "32 32")
            cup.set_prop("value_validation_type", "list")

        chp = self.set_var("current_hdl_parameter", f"[::ipx::add_hdl_parameter {p.name} $top]")

        chp.set_prop("data_type", "integer")
        chp.set_prop("description", f"{p.name}")
        chp.set_prop("display_name", f"{p.name}")
        chp.set_prop("ipxact_id", f"MODELPARAM_VALUE.{p.name}")
        chp.set_prop("order", f"{n}")
        chp.set_prop("value", f"{p.default}")
        chp.set_prop("value_format", "long")
        chp.set_prop("value_resolve_type", "generated")
        chp.set_prop("value_source", "default")
        chp.set_prop("value_validation_type", "range_long")

        self.xgui.cmd("")
        self.xgui.cmd(f"proc update_PARAM_VALUE.{p.name} {{ PARAM_VALUE.{p.name} }} {{")
        self.xgui.cmd("}")

        self.xgui.cmd("")
        self.xgui.cmd(f"proc validate_PARAM_VALUE.{p.name} {{ PARAM_VALUE.{p.name} }} {{")
        self.xgui.cmd(" return true;")
        self.xgui.cmd("}")

        self.xgui.cmd("")
        self.xgui.cmd(f"proc update_MODELPARAM_VALUE.{p.name} {{ MODELPARAM_VALUE.{p.name} PARAM_VALUE.{p.name} }} {{")
        self.xgui.cmd(f"set_property value [get_property value ${{PARAM_VALUE.{p.name}}}] ${{MODELPARAM_VALUE.{p.name}}}")
        self.xgui.cmd("}")
        

    def generate_port(self, n, port_name):
        self.comment(f"Port {port_name}")

        p = self.module.ports[port_name]
        
        cp = self.set_var("current_port", f"[::ipx::add_port {port_name} $top]")
        
        cp.set_prop("direction", "out" if p.direction == "output" else "in")
        cp.set_prop("latency", 0)

        if p.datatype.vector:
            left = p.datatype.packed_range.left
            right = p.datatype.packed_range.right
                
            left_default = int(str(left.subst(self.default_dict)))
            right_default = int(str(right.subst(self.default_dict)))

            cp.set_prop("size_left", left_default)
            
            if not left.const:
                cp.set_prop("size_left_dependency", left.subst(self.model_param_refs))
                cp.set_prop("size_left_resolve_type", "dependent")

            if not (right.const and right_default == '0'):
                cp.set_prop("size_right", right_default)
            
                if not right.const:
                    cp.set_prop("size_right_dependency", right.subst(self.model_param_refs))
                    cp.set_prop("size_right_resolve_type", "dependent")

        cp.set_prop("type_name", "wire")
        cp.set_prop("view_name_refs", "xilinx_verilogsynthesis xilinx_verilogbehavioralsimulation");

    def generate_interface(self, i):
        self.comment(f"Generating interface {i.busname}")

        cbi = self.set_var("current_bus_interface", f"[::ipx::add_bus_interface {i.busname} $top]")

        cbi.set_prop("bus_type_vendor", f"{i.desc.ipxdesc.busType.vendor}")
        cbi.set_prop("bus_type_library", f"{i.desc.ipxdesc.busType.library}")
        cbi.set_prop("bus_type_name", f"{i.desc.ipxdesc.busType.name}")
        cbi.set_prop("bus_type_version", f"{i.desc.ipxdesc.busType.version}")
        cbi.set_prop("bus_type_vlnv", f"{i.desc.ipxdesc.busType.vlnv}")
        cbi.set_prop("abstraction_type_vendor", f"{i.desc.ipxdesc.abstractionType.vendor}")
        cbi.set_prop("abstraction_type_library", f"{i.desc.ipxdesc.abstractionType.library}")
        cbi.set_prop("abstraction_type_name", f"{i.desc.ipxdesc.abstractionType.name}")
        cbi.set_prop("abstraction_type_version", f"{i.desc.ipxdesc.abstractionType.version}")
        cbi.set_prop("abstraction_type_vlnv", f"{i.desc.ipxdesc.abstractionType.vlnv}")

        if i.desc.ipxdesc.memoryMapped:
            if i.modport.name == "SUBORDINATE":
                cbi.set_prop("master_base_address", f"0")
                cbi.set_prop("slave_memory_map_ref", f"{i.busname}")
                cbi.set_prop("monitor_interface_mode", f"master")

                cmm = self.set_var("current_memory_map", f"[::ipx::add_memory_map {i.busname} $top]")

                cab = self.set_var("current_address_block", f"[::ipx::add_address_block {i.busname}_{i.desc.ipxdesc.mmtype} $current_memory_map]")
                
                cab.set_prop("base_address", "0")
                cab.set_prop("base_address_resolve_type", "user")
                cab.set_prop("range", "4096")
                cab.set_prop("width", "32")
                cab.set_prop("usage", "register" if i.desc.ipxdesc.mmtype == "reg" else "memory")

                cabp = self.set_var("cur_address_block_parameter", "[::ipx::add_address_block_parameter OFFSET_BASE_PARAM $current_address_block]")

                cabp = self.set_var("cur_address_block_parameter", "[::ipx::add_address_block_parameter OFFSET_HIGH_PARAM $current_address_block]")
            elif i.modport.name == "MANAGER":
                raise Exception(f"Can't do memory mapped masters yet")                
            else:
                raise Exception(f"Unknown interface to infer for {i.modport.name}")
        else:
            if i.modport.name == "SUBORDINATE":
                cbi.set_prop("interface_mode", f"slave")
            elif i.modport.name == "MANAGER":
                cbi.set_prop("interface_mode", f"master")
            else:
                raise Exception(f"Unknown interface to infer for {i.modport.name}")

        for p in i.data_map:
            logical_port = i.ipxdesc.port_map[i.data_map[p].name]

            cpm = self.set_var("current_port_map", "[::ipx::add_port_map {logical_port} $current_bus_interface]")
            
            cpm.set_prop("logical_name", logical_port)
            cpm.set_prop("physical_name", p)
            cpm.set_prop("is_logical_vector", "false")
            cpm.set_prop("is_physical_vector", "false")

        if i.reset is not None:
            cbi = self.set_var("current_bus_interface", f"[::ipx::add_bus_interface {i.busname}_RST $top];")
            cbi.set_prop("bus_type_vendor", "xilinx.com")
            cbi.set_prop("bus_type_library", "signal")
            cbi.set_prop("bus_type_name", "reset")
            cbi.set_prop("bus_type_version", "1.0")
            cbi.set_prop("bus_type_vlnv", "xilinx.com:signal:reset:1.0")
            cbi.set_prop("abstraction_type_vendor", "xilinx.com")
            cbi.set_prop("abstraction_type_library", "signal")
            cbi.set_prop("abstraction_type_name", "reset_rtl")
            cbi.set_prop("abstraction_type_version", "1.0")
            cbi.set_prop("abstraction_type_vlnv", "xilinx.com:signal:reset_rtl:1.0")
            cbi.set_prop("master_base_address", "0")
            cbi.set_prop("monitor_interface_mode", "master")
            # Add bus_parameter objects
            cbp = self.set_var("current_bus_parameter", "[::ipx::add_bus_parameter POLARITY $current_bus_interface]")
            cbp.set_prop("ipxact_id", f"BUSIFPARAM_VALUE.{i.busname}_RST.POLARITY")
            cbp.set_prop("usage", "all")
            cbp.set_prop("order", "0.000000")
            cbp.set_prop("value", "ACTIVE_LOW" if i.desc.ipxdesc.reset.polarity == "low" else "ACTIVE_HIGH")
            cbp.set_prop("value_source", "constant")
            cbp.set_prop("value_validation_type", "none")
            # Add port_map objects

            cpm = self.set_var("current_port_map", "[::ipx::add_port_map RST $current_bus_interface]")
            cpm.set_prop("logical_name", "RST")
            cpm.set_prop("physical_name", i.reset)
            cpm.set_prop("is_logical_vector", "false")
            cpm.set_prop("is_physical_vector", "false")
            
            
        if i.clock is not None:
            cbi = self.set_var("current_bus_interface", f"[::ipx::add_bus_interface {i.busname}_CLK $top]")

            cbi.set_prop("bus_type_vendor", "xilinx.com")
            cbi.set_prop("bus_type_library", "signal")
            cbi.set_prop("bus_type_name", "clock")
            cbi.set_prop("bus_type_version", "1.0")
            cbi.set_prop("bus_type_vlnv", "xilinx.com:signal:clock:1.0")
            cbi.set_prop("abstraction_type_vendor", "xilinx.com")
            cbi.set_prop("abstraction_type_library", "signal")
            cbi.set_prop("abstraction_type_name", "clock_rtl")
            cbi.set_prop("abstraction_type_version", "1.0")
            cbi.set_prop("abstraction_type_vlnv", "xilinx.com:signal:clock_rtl:1.0")
            cbi.set_prop("master_base_address", "0")
            cbi.set_prop("monitor_interface_mode", "master")

            cbp = self.set_var("current_bus_parameter", "[::ipx::add_bus_parameter ASSOCIATED_BUSIF $current_bus_interface]")
            cbp.set_prop("description", "List of bus interface names separated by colons. For example, m_axis_a:s_axis_b:s_axis_c")
            cbp.set_prop("ipxact_id", "BUSIFPARAM_VALUE.S00_AXI_CLK.ASSOCIATED_BUSIF")
            cbp.set_prop("usage", "all")
            cbp.set_prop("order", "0.000000")
            cbp.set_prop("value", f"{i.busname}")
            cbp.set_prop("value_source", "constant")
            cbp.set_prop("value_validation_type", "none")
            
            cbp = self.set_var("current_bus_parameter", "[::ipx::add_bus_parameter ASSOCIATED_RESET $current_bus_interface]")
            cbp.set_prop("ipxact_id", "BUSIFPARAM_VALUE.S00_AXI_CLK.ASSOCIATED_RESET")
            cbp.set_prop("usage", "all")
            cbp.set_prop("order", "0.000000")
            cbp.set_prop("value", f"{i.reset}")
            cbp.set_prop("value_source", "constant")
            cbp.set_prop("value_validation_type", "none")

            # Add port_map objects
            cpm = self.set_var("current_port_map", "[::ipx::add_port_map CLK $current_bus_interface]")
            cpm.set_prop("logical_name", "CLK")
            cpm.set_prop("physical_name", f"{i.clock}")
            cpm.set_prop("is_logical_vector", "false")
            cpm.set_prop("is_physical_vector", "false")

