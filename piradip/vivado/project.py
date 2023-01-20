from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys
import re
from functools import cached_property

from piradip.boards.SDRv2 import *

from .process import TCLVivadoWrapper

from .obj import VivadoObj
from .bd import *



class BoardComponent(VivadoObj):
    def __init__(self, board, name):
        super().__init__(board, name)

    @property
    def obj(self):
        return "[get_board_components {self.name}]"

    @cached_property
    def modes(self):
        return self.cmd(f"get_board_component_modes -of_object {self.obj}")

    @cached_property
    def ip_preferences(self):
        pass

class Board(VivadoObj):
    def __init__(self, project):
        super().__init__(project, self.board_id)
        project.set_property("platform.board_id", self.board_id)
        project.set_property("board_part", self.part)

    @property
    def obj(self):
        return "[ current_board ]"

    @property
    def parameters(self):
        return self.cmd("get_board_parameters").split()


    @cached_property
    def components(self):
        return [ BoardComponent(self, n) for n in self.cmd("get_board_components").split() ]

    
    @property
    def part(self):
        return self.cmd("current_board_part")


class ZCU111(Board):
    fpga = "xczu28dr-ffvg1517-2-e"
    part = "xilinx.com:zcu111:part0:1.4"
    board_id = "zcu111"
    


class Fileset(VivadoObj):
    def __init__(self, project, name, fstype="srcset"):
        super().__init__(project, name)
        self.fstype = fstype
        l = self.cmd(f"get_filesets {self.name}").split()

        if len(l) == 0:                     
            self.cmd(f"create_fileset -{self.fstype} {self.name}")
            
    @property
    def obj(self):
        return f"[get_filesets {self.name}]"

    def add_file(self, path):
        self.cmd(f"add_files -fileset {self.name} [list [file normalize \"{path}\"]]")

class ReportConfig(VivadoObj):
    def __init__(self, parent, name, rpt_type, steps):
        super().__init__(parent, name)
        parent.reports.append(self)
        self.rpt_type = rpt_type
        self.steps = steps
        self.cmd(f"create_report_config -report_name {self.name} -report_type {self.rpt_type} -steps {self.steps} -runs {self.parent.name}")

    @property
    def obj(self):
        return f"[get_report_configs -of_objects {self.parent.obj} {self.name}]"
        
class Run(VivadoObj):
    def __init__(self, parent, name, run_type, flow, strategy, report_strategy, parent_run=None):
        super().__init__(parent, name)
        self.run_type = run_type
        self.flow = flow
        self.strategy = strategy
        self.report_strategy = report_strategy
        self.reports = list()
        
        s = f"create_run -name {self.name} -part {self.parent.board.fpga} -flow {{{self.flow}}}"
        s += f" -strategy \"{self.strategy}\""
        s += f" -report_strategy {{{self.report_strategy}}}"
        s += f" -constrset {self.parent.constraint_fileset.name}"

        if parent_run is not None:
            s += f" -parent_run {parent_run}"
        
        self.cmd(s)

    @property
    def obj(self):
        return f"[get_runs {self.name}]"
        
    def make_current(self):
        self.cmd(f"current_run -{self.run_type} {self.obj}")

    def make_report(self, name, rpt_type, steps):
        return ReportConfig(self, name, rpt_type, steps)
    
class Project(VivadoObj):
    def __init__(self, vivado, name):
        self.vivado = vivado
        self.board = self.board_cls(self)

        super().__init__(None, name)

        self.src_fileset = Fileset(self, "sources_1")
        self.constraint_fileset =  Fileset(self, "constraints", "constrset")
        self.simulation_fileset = Fileset(self, "simulations", "simset")

    def build_project(self):
        self.set_default_properties()

        self.project_dir = Path.cwd()
    
        print(f"Creating project {name} in {self.project_dir}...")

        self.sources_dir = self.project_dir / "sources"
        self.constraints_dir = self.project_dir / "constraints"

        self.sources_dir.mkdir(exist_ok=True)
        self.constraints_dir.mkdir(exist_ok=True)

        self.constraints_filename = self.constraints_dir / f"{name}.xdc"

        self.constrints_file = open(self.constraints_filename, "w+")


        piradip_root = Path(__file__).parent.parent.parent

        common_path = Path(os.path.commonpath((piradip_root, self.project_dir)))

        print(piradip_root)
        print(f"Common Path: {common_path}")
        
        s = ""

        while not (self.project_dir/s).samefile(common_path):
            s += "../"
        
        modpath = Path(s) / piradip_root.relative_to(common_path)

        print(f"Relative IP repo path: {modpath}")
        
        self.src_fileset.set_property("ip_repo_paths", f"[file normalize \"{modpath}\"]")

        self.cmd("update_ip_catalog -rebuild")
    
        self.src_fileset.set_property("dataflow_viewer_settings", "min_width=16")


        self.constraint_fileset.add_file(self.constraints_filename)

        
        self.simulation_fileset.set_property("top_lib", "xil_defaultlib")
        

    @classmethod
    def load(cls, vivado, name):
        vivado.cmd(f"open_project {name}.xpr")

        return cls(vivado, name)
        
    @classmethod
    def create(cls, vivado, name):
        vivado.cmd(f"create_project -force {name}.xpr ./ -part {cls.board_cls.fpga}", timeout=90)

        prj = cls(vivado, name)
        
        prj.build_project()

        return prj
        
        
    @property
    def obj(self):
        return "[current_project]"
        
    def set_default_properties(self):
        self.set_property("default_lib", "xil_defaultlib")
        self.set_property("enable_resource_estimation", 0)
        self.set_property("enable_vhdl_2008", 1)
        self.set_property("ip_cache_permissions", "read write")
        self.set_property("ip_output_repo", f"ip_cache")
        self.set_property("mem.enable_memory_map_generation", "1")
        self.set_property("revised_directory_structure", "1")
        self.set_property("sim.central_dir", "ip_user_files")
        self.set_property("sim.ip.auto_export_scripts", "1")
        self.set_property("simulator_language", "Mixed")
        self.set_property("sim_compile_state", "1")
        self.set_property("webtalk.activehdl_export_sim", "49")
        self.set_property("webtalk.modelsim_export_sim", "49")
        self.set_property("webtalk.questa_export_sim", "49")
        self.set_property("webtalk.riviera_export_sim", "49")
        self.set_property("webtalk.vcs_export_sim", "49")
        self.set_property("webtalk.xsim_export_sim", "49")
        self.set_property("xpm_libraries", "XPM_CDC XPM_FIFO XPM_MEMORY")

    def create_fileset(self, name, fstype="srcset"):
        return Fileset(self, name, fstype)

    
    def create_runs(self):
        self.synth_run = Run(self, "synthesis", "synthesis",
                             flow="Vivado Synthesis 2022",
                             strategy="Vivado Synthesis Defaults",
                             report_strategy="No Reports")

        self.synth_run.set_property("set_report_strategy_name", "1")
        self.synth_run.set_property("report_strategy", "Vivado Synthesis Default Reports")
        self.synth_run.set_property("set_report_strategy_name", "0")
        self.synth_run.make_report("synthesis_utilization_report", "report_utilization:1.0", "synth_design")
        self.synth_run.set_property("needs_refresh", "1")
        #self.synth_run.set_property("incremental_checkpoint", "$proj_dir/140GHz.srcs/utils_1/imports/synth_1/PiRadio_140GHz_wrapper.dcp")
        #self.synth_run.set_property("auto_incremental_checkpoint", "1")
        self.synth_run.set_property("strategy", "Vivado Synthesis Defaults")
        
        # set the current synth run
        self.synth_run.make_current()

        self.impl_run = Run(self, "implementation", "implementation",
                            flow="Vivado Implementation 2022",
                            strategy="Vivado Implementation Defaults",
                            report_strategy="No Reports",
                            parent_run=self.synth_run.name)

        self.impl_run.set_property("set_report_strategy_name", "1")
        self.impl_run.set_property("report_strategy", "Vivado Implementation Default Reports")
        self.impl_run.set_property("set_report_strategy_name", "0")

        rpt = self.impl_run.make_report("initial_timing_summary", "report_timing_summary:1.0", "init_design")
        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("drc_report", "report_drc:1.0", "opt_design")

        rpt = self.impl_run.make_report("opt_timing_summary", "report_timing_summary:1.0", "opt_design")
        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("power_opt_timing_summary", "report_timing_summary:1.0", "power_opt_design")
        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("placement_report", "report_io:1.0", "place_design")

        rpt = self.impl_run.make_report("placement_utilization", "report_utilization:1.0", "place_design")

        rpt = self.impl_run.make_report("impl_1_place_report_utilization_0", "report_utilization:1.0", "place_design")

        rpt = self.impl_run.make_report("impl_1_place_report_control_sets_0", "report_control_sets:1.0", "place_design")
        rpt.set_property("options.verbose", "1")

        rpt = self.impl_run.make_report("impl_1_place_report_incremental_reuse_0", "report_incremental_reuse:1.0", "place_design")
        rpt.set_property("is_enabled", "0")

        rpt = self.impl_run.make_report("impl_1_place_report_incremental_reuse_1", "report_incremental_reuse:1.0", "place_design")
        rpt.set_property("is_enabled", "0")

        rpt = self.impl_run.make_report("impl_1_place_report_timing_summary_0", "report_timing_summary:1.0", "place_design")
        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("impl_1_post_place_power_opt_report_timing_summary_0", "report_timing_summary:1.0", "post_place_power_opt_design")

        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("impl_1_phys_opt_report_timing_summary_0", "report_timing_summary:1.0", "phys_opt_design")

        rpt.set_property("is_enabled", "0")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("impl_1_route_report_drc_0", "report_drc:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_methodology_0", "report_methodology:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_power_0", "report_power:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_route_status_0", "report_route_status:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_timing_summary_0", "report_timing_summary:1.0", "route_design")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")

        rpt = self.impl_run.make_report("impl_1_route_report_incremental_reuse_0", "report_incremental_reuse:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_clock_utilization_0", "report_clock_utilization:1.0", "route_design")

        rpt = self.impl_run.make_report("impl_1_route_report_bus_skew_0", "report_bus_skew:1.1", "route_design")
        rpt.set_property("options.warn_on_violation", "1")

        rpt = self.impl_run.make_report("impl_1_post_route_phys_opt_report_timing_summary_0", "report_timing_summary:1.0", "post_route_phys_opt_design")
        rpt.set_property("options.max_paths", "10")
        rpt.set_property("options.report_unconstrained", "1")
        rpt.set_property("options.warn_on_violation", "1")

        rpt = self.impl_run.make_report("impl_1_post_route_phys_opt_report_bus_skew_0", "report_bus_skew:1.1", "post_route_phys_opt_design")
        rpt.set_property("options.warn_on_violation", "1")

        self.impl_run.set_property("needs_refresh", "1")
        self.impl_run.set_property("strategy", "Vivado Implementation Defaults")
        self.impl_run.set_property("steps.write_bitstream.args.bin_file", "1")
        self.impl_run.set_property("steps.write_bitstream.args.readback_file", "0")
        self.impl_run.set_property("steps.write_bitstream.args.verbose", "0")
        """

# set the current impl run
current_run -implementation [get_runs impl_1]
catch {
 if { $idrFlowPropertiesConstraints != {} } {
   set_param runs.disableIDRFlowPropertyConstraints $idrFlowPropertiesConstraints
 }
}
        """
        self.impl_run.make_current()

        
    
        
class ZCU111Project(Project):
    board_cls = ZCU111
    
    def __init__(self, vivado, name):
        super().__init__(vivado, name)

class NPM:
    def __init__(self, prj):
        self.prj = prj
        
        self.cmd(f"set_part {prj.board.fpga}")
        self.cmd(f"set_property TARGET_LANGUAGE Verilog [current_project]")
        self.cmd(f"set_property BOARD_PART {prj.board.part} [current_project]")
        self.cmd(f"set_property DEFAULT_LIB xil_defaultlib [current_project]")
        self.cmd(f"set_property IP_REPO_PATHS \"../PiRadIP\" [current_fileset]")

        Path("reports").mkdir()
        Path("checkpoints").mkdir()
        
    @cached_property
    def vivado(self):
        return self.prj.vivado

    def cmd(self, cmd, **kwargs):
        return self.vivado.cmd(cmd, **kwargs)

    def read_bd(self):
        self.cmd(f"read_bd {self.prj.bd_path}")

    @property
    def ips(self):
        return self.cmd(f"get_ips").split()

    def ip_locked(self, ip):
        return int(self.cmd(f"get_property IS_LOCKED [get_ips {ip}]")) == 1
    
    def check_ips(self):
        locked = []
        need_save = False
        
        for ip in self.ips:
            if not self.ip_locked(ip):
                continue
            
            details = self.cmd(f"get_property LOCK_DETAILS [get_ips {ip}]")
            print(f"IP {ip} is locked: {details}")    

            self.cmd(f"upgrade_ips [get_ips {ip}]")
            need_save = True
            
            if self.ip_locked(ip):
                details = self.cmd(f"get_property LOCK_DETAILS [get_ips {ip}]")
                locked.append((ip, details))

        if need_save:
            self.cmd("save_bd_design")
                
        return locked

    def load_bd(self):
        self.read_bd()
        locked = self.check_ips()

        if len(locked):
            raise RuntimeError(f"Some IP still locked: {locked}")
        
    def generate(self):
        self.load_bd()
        self.cmd(f"set_property synth_checkpoint_mode None [get_files {self.prj.bd_path}]")
        self.cmd(f"generate_target all [get_files {self.prj.bd_path}]")

    def read_constraints(self):
        self.cmd(f"read_xdc {self.prj.constraints_path}")

    def make_and_read_wrapper(self):
        self.generate()
        self.cmd(f"make_wrapper -files [get_files {self.prj.bd_path}] -top")
        self.cmd(f"read_verilog {self.prj.bd_wrapper}")
        self.cmd(f"update_compile_order -fileset sources_1")

    @property
    def top(self):
        return self.cmd("lindex [find_top] 0")
    
    def read_checkpoint(self, f):
        print(f"Reading checkpoint \"{f}\"...")
        print(self.cmd(f"open_checkpoint \"{f}\""))
    
    def synthesize(self):
        self.make_and_read_wrapper()

        self.cmd(f"set_property top {self.top} [current_fileset]")
        self.cmd(f"set_property XPM_LIBRARIES {{XPM_CDC XPM_MEMORY XPM_FIFO}} [current_project]")
        self.cmd(f"synth_design -top {self.top} -flatten_hierarchy none", timeout=12*60*60)

        self.cmd(f"write_checkpoint checkpoints/synthesis.dcp")

        
        self.cmd(f"report_timing_summary -file reports/synthesis_timing.rpt")
        
    def optimize(self, checkpoint=None):
        if checkpoint is not None:
            self.read_checkpoint(checkpoint)
        else:
            self.synthesize()

        self.cmd(f"opt_design")

        self.cmd(f"write_checkpoint checkpoints/optimized.dcp")
        self.cmd(f"report_timing_summary -file reports/opt_timing.rpt")

        
    def place(self, checkpoint=None):
        if checkpoint is not None:
            self.read_checkpoint(checkpoint)
        else:
            self.optimize()

        self.cmd(f"place_design")
        self.cmd(f"write_checkpoint checkpoints/placed.dcp")
        self.cmd(f"phys_opt_design")
        self.cmd(f"write_checkpoint checkpoints/popt.dcp")

        self.cmd(f"report_timing_summary -file reports/placed_timing.rpt")

    def route(self, checkpoint=None):
        if checkpoint is not None:
            self.read_checkpoint(checkpoint)
        else:
            self.place()

        self.cmd(f"route_design")
        self.cmd(f"write_checkpoint checkpoints/routed.dcp")
        self.cmd(f"report_timing_summary -file reports/routed_timing.rpt")
    
    def write_bitstream(self, checkpoint=None):
        if checkpoint is not None:
            self.read_checkpoint(checkpoint)
        else:
            self.route()

        #self.cmd(f"opt_design")

    def write_xsa(self, checkpoint=None):
        if checkpoint is not None:
            self.read_checkpoint(checkpoint)
        else:
            self.route()

        #self.cmd(f"opt_design")
        

            
class PiRadioProject:
    base_project = ZCU111Project
    bd_template = SDRv2_Capture

    @property
    def board(self):
        return self.base_project.board_cls

    @cached_property
    def NPM(self):
        return NPM(self)
    
    def __init__(self):
        self.vivado = TCLVivadoWrapper()

    def cmd(self, cmd, **kwargs):
        return self.vivado.cmd(cmd, **kwargs)

    def open(self):
        self.prj = self.base_project.load(self.vivado, self.project_name)
    
    def create(self):
        self.prj = self.base_project.create(self.vivado, self.project_name)

        for ip in [ "xilinx.com:ip:proc_sys_reset:5.0",
                    "xilinx.com:ip:xlconcat:2.1",
                    "xilinx.com:ip:xlslice:1.0",
                    "xilinx.com:ip:zynq_ultra_ps_e:3.4",
                    "xilinx.com:ip:clk_wiz:6.0",
                    "xilinx.com:ip:usp_rf_data_converter:2.6",
                    "xilinx.com:ip:util_vector_logic:2.0",
                    "pi-rad.io:piradip:axis_sample_buffer_in:1.0",
                    "pi-rad.io:piradip:axis_sample_buffer_out:1.0",
                    "pi-rad.io:piradip:axis_sample_interleaver:1.0",
                    "pi-rad.io:piradip:piradip_slice32:1.0",
                    "pi-rad.io:piradip:piradip_trigger_unit:1.0", ]:
            self.vivado.cmd(f"get_ipdefs -all {ip}")
        
        self.bd = self.bd_template(self.prj, self.project_name)

        self.bd.assign_addresses()
    
        try:
            self.bd.validate()
        except Exception as e:
            print("Validation failed")
        
        self.bd.save()
        self.bd.dump_properties()
        self.bd.close()
        self.bd.wrap()
        self.bd.generate()
        
    def create_runs(self):
        self.prj.create_runs()
        
        
    @property
    def bd_path(self):
        return f"block-design/{self.project_name}/{self.project_name}.bd"

    @property
    def bd_wrapper(self):
        return f"block-design/{self.project_name}/hdl/{self.project_name}_wrapper.v"

    @property
    def constraints_path(self):
        return f"constraints/{self.project_name}.xdc"

        

    
    """
set idrFlowPropertiesConstraints ""
catch {
 set idrFlowPropertiesConstraints [get_param runs.disableIDRFlowPropertyConstraints]
 set_param runs.disableIDRFlowPropertyConstraints 1
}
    """
