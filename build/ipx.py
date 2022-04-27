from .piradip_build_base import *

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
    def __init__(self, f):
        self._tcl_body = f
        self._indent = 0

    def cmd(self, v):
        self._tcl_body.write(f"{self.indent_string}{v}\n")

    def indent(self):
        self._indent += 1

    def deindent(self):
        self._indent -= 1

    def blank(self):
        self._tcl_body.write("\n")

    @property
    def indent_string(self):
        return 4*self._indent*" "

    def get_var(self, v):
        return TCLVar(self, v)

    def set_var(self, var, value):
        self.cmd(f"set {var} {value};")
        return TCLVar(self, var)

    def comment(self, c):
        self.cmd(f"# {c}")


class IPXScript(TCLScript):
    def __init__(self, module, f):
        super(IPXScript, self).__init__(f)
        self.module = module
        self.desc = module.desc
        self.n = 0
        self.param_ids = {}
        self.model_param_ids = {}
        self.model_param_refs = {}
        self.default_dict = {}

    def generate(self):
        self.comment("Create component")
        self.cmd(f"set prev_path [pwd]")
        self.cmd(f"cd \"{self.desc.wrapper_path}\"")
        self.cmd(f"ipx::create_core {vendor} {library} {self.desc.wrapper_name} {self.desc.version}")



        for p in self.module.exposed_params:
            self.param_ids[p] = svsymbol(f"PARAM_VALUE.{p}")
            self.model_param_ids[p] = svsymbol(f"MODELPARAM_VALUE.{p}")
            self.model_param_refs[p] = svsymbol(f"spirit:decode(id('{self.model_param_ids[p]}'))")

        for p in self.module.outer_params:
            self.default_dict[p] = self.module.outer_params[p].default

        known_symbols = set(self.default_dict.keys())

        while not all([ x.const for x in self.default_dict.values()]):
            unresolved = set()

            for p in self.default_dict:
                unresolved |= self.default_dict[p].unresolved

            if (unresolved - known_symbols) != set():
                ERROR(f"Unhandled symbols: {unresolved - known_symbols}")

            for p in self.default_dict:
                if not self.default_dict[p].const:
                    self.default_dict[p] = subst(self.default_dict[p], self.default_dict)

        top = self.set_var("top", "[ipx::current_core]")

        self.comment("")
        self.comment("Define globals")
        self.comment("")

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

        self.comment("")
        self.comment("Generate ports")
        self.comment("")

        for n, p in enumerate(sorted(self.module.outer_ports)):
            self.generate_port(n, p)


        self.comment("")
        self.comment("Generate parameters")
        self.comment("")

        for n, p in enumerate(sorted(self.module.exposed_params)):
            self.generate_parameter(n, self.module.outer_params[p])


        self.comment("")
        self.comment("Generate interfaces")
        self.comment("")

        if self.module.has_interfaces:
            for i in self.module.interface_ports.values():
                if i.desc.ipxdesc is not None:
                    self.generate_interface(i)

        self.comment("")
        self.comment("Add file groups")
        self.comment("")

        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_verilogsynthesis $top]")
        cfg.set_prop("display_name", "Verilog Synthesis")
        cfg.set_prop("language", "verilog")
        cfg.set_prop("model_name", self.module.name)
        cfg.set_prop("env_ids", "verilogSource:vivado.xilinx.com:synthesis")

        cf = self.set_var("current_file", f"[::ipx::add_file {self.desc.wrapper_verilog_relpath} $current_file_group]")
        cf.set_prop("type", "verilogSource")
        cf.set_prop("processing_order", "normal")


        self.cmd("ipx::add_subcore pi-rad.io:library:PiRadIP:1.0 [ipx::get_file_groups xilinx_verilogsynthesis -of_objects [ipx::current_core]]")
        
        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_verilogsimulation $top]")
        cfg.set_prop("display_name", "Verilog Simulation")
        cfg.set_prop("language", "verilog")
        cfg.set_prop("model_name", self.module.name)
        cfg.set_prop("env_ids", "verilogSource:vivado.xilinx.com:simulation")

        cf = self.set_var("current_file", f"[::ipx::add_file {self.desc.wrapper_verilog_relpath} $current_file_group]")
        cf.set_prop("type", "verilogSource")
        cf.set_prop("processing_order", "normal")

        self.cmd("ipx::add_subcore pi-rad.io:library:PiRadIP:1.0 [ipx::get_file_groups xilinx_verilogsimulation -of_objects [ipx::current_core]]")
        
        cfg = self.set_var("current_file_group", "[::ipx::add_file_group xilinx_xpgui $top]")
        cfg.set_prop("display_name", "UI Layout")
        cfg.set_prop("env_ids", ":vivado.xilinx.com:xgui.ui")

        cf = self.set_var("current_file", f"[::ipx::add_file {self.module.desc.wrapper_xgui_relpath} $current_file_group]")
        cf.set_prop("type", "tclSource")
        cf.set_prop("processing_order", "normal")
        cf.set_prop("xgui_version", "2")

        cfg = self.set_var("current_file_group", "[::ipx::add_file_group bd_tcl $top]")
        cfg.set_prop("display_name", "Block Diagram")
        cfg.set_prop("env_ids", ":vivado.xilinx.com:block.diagram")

        cf = self.set_var("current_file", "[::ipx::add_file bd/bd.tcl $current_file_group]")
        cf.set_prop("type", "tclSource")
        cf.set_prop("processing_order", "normal")

        self.cmd("ipx::save_core [ipx::current_core]")

        self.cmd("ipx::unload_core [ipx::current_core]")
        self.cmd("cd $prev_path")

    def generate_parameter(self, n, p):

        self.comment("")
        self.comment(f"Parameter {p.name}")
        self.comment("")

        self.blank()
        self.comment("User parameter")
        cup = self.set_var("current_user_parameter", f"[::ipx::add_user_parameter {p.name} $top]")

        self.indent()

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

        if len(p.allowed_values):
            cup.set_prop("value_validation_list", " ".join([f"{av}" for av in p.allowed_values]))
            cup.set_prop("value_validation_pairs", " ".join([f"{av} {av}" for av in p.allowed_values]))
            cup.set_prop("value_validation_type", "list")

        self.deindent()

        self.blank()
        self.comment("HDL parameter")
        chp = self.set_var("current_hdl_parameter", f"[::ipx::add_hdl_parameter {p.name} $top]")

        self.indent()

        chp.set_prop("data_type", "integer")
        chp.set_prop("description", f"{p.name}")
        chp.set_prop("display_name", f"{p.name}")
        chp.set_prop("ipxact_id", f"MODELPARAM_VALUE.{p.name}")
        chp.set_prop("order", f"{n}")
        chp.set_prop("value", p.default)
        chp.set_prop("value_format", "long")
        chp.set_prop("value_resolve_type", "generated")
        chp.set_prop("value_source", "default")
        chp.set_prop("value_validation_type", "range_long")

        self.deindent()




    def generate_port(self, n, port_name):
        self.comment("")
        self.comment(f"Port {port_name}")
        self.comment("")

        p = self.module.outer_ports[port_name]

        cp = self.set_var("current_port", f"[::ipx::add_port {port_name} $top]")

        cp.set_prop("direction", "out" if p.direction == "output" else "in")
        cp.set_prop("latency", 0)
        
        if p.datatype.vector:
            self.comment("")
            self.comment("Vector parameters")
            self.comment("")
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
        self.comment("")
        self.comment(f"Generating interface {i.busname}")
        self.comment("")

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

        for xp in i.desc.ipxdesc.xilinxParameters:
            cbp = self.set_var("current_bus_parameter", f"[::ipx::add_bus_parameter {xp.name} $current_bus_interface]")

            cbp.set_prop("ipxact_id", xp.ipxact_id.format(**locals()))
            cbp.set_prop("usage", xp.usage);
            cbp.set_prop("order", xp.order);
            cbp.set_prop("value", xp.default_value);
            cbp.set_prop("value_format", xp.value_format);
            cbp.set_prop("value_source", xp.value_source);

            if len(xp.allowed_values):
                cbp.set_prop("value_validation_list", " ".join([f"{v}" for v in xp.allowed_values]));
                cbp.set_prop("value_validation_pairs", " ".join([f"{v} {v}" for v in xp.allowed_values]));
                cbp.set_prop("value_validation_type", "list");

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


class XilinxXGUITcl(TCLScript):
    def __init__(self, module, f):
        super(XilinxXGUITcl, self).__init__(f)
        self.module = module

    def generate(self):
        self.cmd("proc init_gui { IPINST } {")
        self.cmd(" ipgui::add_param $IPINST -name \"Component_Name\"")
        self.cmd(" set Page_0 [ipgui::add_page $IPINST -name \"Page 0\"]")

        for p in self.module.outer_params.values():
            # ipgui::add_param $IPINST -name "C_S01_AXI_ID_WIDTH" -parent ${Page_0}
            # ipgui::add_param $IPINST -name "C_S01_AXI_DATA_WIDTH" -parent ${Page_0} -widget comboBox
            self.cmd(f"ipgui::add_param $IPINST -name \"{p.name}\" -parent ${{Page_0}}")  #add combobox
        
        self.cmd("}")


        for p in self.module.outer_params.values():
            self.cmd("")
            self.cmd(f"proc update_PARAM_VALUE.{p.name} {{ PARAM_VALUE.{p.name} }} {{")
            self.cmd("}")

            self.cmd("")
            self.cmd(f"proc validate_PARAM_VALUE.{p.name} {{ PARAM_VALUE.{p.name} }} {{")
            self.cmd(" return true;")
            self.cmd("}")

            self.cmd("")
            self.cmd(f"proc update_MODELPARAM_VALUE.{p.name} {{ MODELPARAM_VALUE.{p.name} PARAM_VALUE.{p.name} }} {{")
            self.cmd(f"set_property value [get_property value ${{PARAM_VALUE.{p.name}}}] ${{MODELPARAM_VALUE.{p.name}}}")
            self.cmd("}")

class XilinxBDTcl(TCLScript):
    def __init__(self, module, f):
        super(XilinxBDTcl, self).__init__(f)
        self.module = module

    def generate(self):
        self.cmd("proc init { cellpath otherInfo } {")
        self.indent()
        self.cmd("puts \"bd init proc\"")
        self.cmd("set cell_handle [get_bd_cells $cellpath]")
        self.cmd("set all_busif [get_bd_intf_pins $cellpath/*]")
        self.cmd("set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]")
        self.cmd("set full_sbusif_list [list  AXIMM ]")
        self.blank()
        self.cmd("foreach busif $all_busif {")
        self.indent()
        self.cmd("if { [string equal -nocase [get_property MODE $busif] \"slave\"] == 1 } {")
        self.cmd("set busif_param_list [list]")
        self.cmd("set busif_name [get_property NAME $busif]")
        self.cmd("if { [lsearch -exact -nocase $full_sbusif_list $busif_name ] == -1 } {")
        self.cmd("continue")
        self.cmd("}")
        self.cmd("foreach tparam $axi_standard_param_list {")
        self.cmd("lappend busif_param_list \"C_${busif_name}_${tparam}\"")

        self.cmd("}")
        self.cmd("bd::mark_propagate_only $cell_handle $busif_param_list")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("proc pre_propagate {cellpath otherInfo } {")
        self.cmd("puts \"bd pre_propagate proc\"")
        self.cmd("set cell_handle [get_bd_cells $cellpath]")
        self.cmd("set all_busif [get_bd_intf_pins $cellpath/*]")
        self.cmd("set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]")
        self.cmd("foreach busif $all_busif {")
        self.cmd("if { [string equal -nocase [get_property CONFIG.PROTOCOL $busif] \"AXI4\"] != 1 } {")
        self.cmd("continue")
        self.cmd("}")
        self.cmd("if { [string equal -nocase [get_property MODE $busif] \"master\"] != 1 } {")
        self.cmd("continue")
        self.cmd("}")
        self.cmd("set busif_name [get_property NAME $busif]")
        self.cmd("foreach tparam $axi_standard_param_list {")
        self.cmd("set busif_param_name \"C_${busif_name}_${tparam}\"")
        # puts line
        self.cmd("puts \"PIRADIO: pre-propagate  Setting busif param name to ${busif_name}_${tparam}\"")
        self.cmd("set val_on_cell_intf_pin [get_property CONFIG.${tparam} $busif]")
        self.cmd("set val_on_cell [get_property CONFIG.${busif_param_name} $cell_handle]")
        self.cmd("if { [string equal -nocase $val_on_cell_intf_pin $val_on_cell] != 1 } {")
        self.cmd("if { $val_on_cell != \"\" } {")
        self.cmd("set_property CONFIG.${tparam} $val_on_cell $busif")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("proc propagate {cellpath otherInfo } {")
        self.cmd("puts \"bd propagate proc\"")
        self.cmd("set cell_handle [get_bd_cells $cellpath]")
        self.cmd("set all_busif [get_bd_intf_pins $cellpath/*]")
        self.cmd("set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]")
        self.cmd("foreach busif $all_busif {")
        self.cmd("puts \"Propagate ${axi_standard_param_list}\"")
        self.cmd("if { [string equal -nocase [get_property CONFIG.PROTOCOL $busif] \"AXI4\"] != 1 } {")
        self.cmd("continue")
        self.cmd("}")
        self.cmd("if { [string equal -nocase [get_property MODE $busif] \"slave\"] != 1 } {")
        self.cmd("continue")
        self.cmd("}")
        self.cmd("set busif_name [get_property NAME $busif]")
        self.cmd("foreach tparam $axi_standard_param_list {")
        self.cmd("set busif_param_name \"C_${busif_name}_${tparam}\"")
        # puts line
        self.cmd("puts \"PIRADIO: propagate  Setting busif param name to ${busif_name}_${tparam}\"")
        self.cmd("")
        self.cmd("set val_on_cell_intf_pin [get_property CONFIG.${tparam} $busif]")
        self.cmd("set val_on_cell [get_property CONFIG.${busif_param_name} $cell_handle]")
        self.cmd("")
        self.cmd("if { [string equal -nocase $val_on_cell_intf_pin $val_on_cell] != 1 } {")
        self.cmd("#override property of bd_interface_net to bd_cell -- only for slaves.  May check for supported values..")
        self.cmd("if { $val_on_cell_intf_pin != \"\" } {")
        self.cmd("set_property CONFIG.${busif_param_name} $val_on_cell_intf_pin $cell_handle")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
        self.cmd("}")
