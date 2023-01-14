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

from .piradip_build_base import *
from .bd import *

from .SDRv2 import *

DEBUG=False

class TCLVivadoWrapper:
    msg_re = re.compile(f"(?P<level>ERROR|WARNING|INFO): \[(?P<facility>[^\s]+) (?P<maj>[\d]+)-(?P<min>[\d]+)\] (?P<msg>.*)")
    
    def __init__(self):
        INFO("Launching background Vivado process")
        kwargs = {}

        if log_vivado:
           kwargs["logfile"] = sys.stdout
            
        self.p = pexpect.spawnu("vivado -nolog -nojournal -notrace -mode tcl", **kwargs)
        self.p.expect("Vivado%", timeout=60)

        self.msg_history = []
        
    def write(self, line, timeout=30, echo=False):
        if line[0] == '#':
            return
        #print(line, end="")
        self.cmd_msgs = []
        self.p.send(line)

        if echo:
            print(line)
        
        r = self.p.readline()

        if DEBUG:
            print(f"COMMAND: {line}")
            print(f"ECHO: {r}")
            
        retval = ""

        die = False
        
        while True:
            v = self.p.expect(["Vivado%", "INFO:.*\n", "WARNING:.*\n", "ERROR:.*\n"], timeout=timeout)

            if echo:
                print(self.p.before + self.p.after)
            
            if DEBUG:
                print(f"RESULT: {v} {self.p.after}")
            
            if v == 0:
                retval += self.p.before
                break
            else:
                s = self.p.after.strip()

                print(s)
                
                m = self.msg_re.match(s)

                if m is not None:
                    self.cmd_msgs.append((m['level'], m['facility'], m['maj'], m['min'], m['msg']))
                else:
                    assert v == 1
                    self.cmd_msgs.append(('INFO', s))
                    
                if v >= 3:
                    die = True

        self.msg_history.append((line, self.cmd_msgs))
                
        if die:
            print(f"Error Command: {line}")
            raise Exception("Vivado error")
                
        if DEBUG:
            print(f"RETVAL: {retval}")
        return retval.strip()

    def cmd(self, line, **kwargs):
        return self.write(f"{line}\n", **kwargs)

    def set_property(self, prop, val, obj):
        self.cmd(f"set_property -name \"{prop}\" -value \"{val}\" -objects {obj}")

def create_project(name):
    t = TCLVivadoWrapper()

    project_dir = Path.cwd()
    
    print(f"Creating project {name} in {project_dir}...")

    sources_dir = project_dir / "sources"
    
    constraints_dir = project_dir / "constraints"

    sources_dir.mkdir(exist_ok=True)
    constraints_dir.mkdir(exist_ok=True)

    constraints_file = constraints_dir / f"{name}.xdc"
    
    with open(constraints_file, "w") as f:
        pass

    wrapper_name = f"{name}_wrapper"

    class BoardComponent:
        def __init__(self, board, name):
            self.board = board
            self.name = name

        @property
        def obj(self):
            return "[get_board_components {self.name}]"

        @cached_property
        def modes(self):
            return t.cmd(f"get_board_component_modes -of_object {self.obj}")

        @cached_property
        def ip_preferences(self):
            pass
    
    class Board:
        def __init__(self, project):
            self.project = project

        @property
        def obj(self):
            return "[ current_board ]"
            
        @property
        def parameters(self):
            return t.cmd("get_board_parameters").split()

        
        @cached_property
        def components(self):
            return [ BoardComponent(self, n) for n in t.cmd("get_board_components").split() ]

        @property
        def part(self):
            return t.cmd("current_board_part")

            
            
    class Project:
        def __init__(self, name, fpga, board):
            t.cmd(f"create_project -force {name}.xpr ./ -part {fpga}", timeout=90)
            self.set_property("board_part", board)
            
        def set_property(self, prop, val):
            t.set_property(prop, val, "[current_project]")

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
            
    class ZCU111Project(Project):
        def __init__(self, name):
            super().__init__(name, "xczu28dr-ffvg1517-2-e", "xilinx.com:zcu111:part0:1.4")
            self.set_property("platform.board_id", "zcu111")

    class Fileset:
        def __init__(self, name, fstype="srcset"):
            self.name = name
            t.cmd(f"create_fileset -{fstype} {name}")

        def set_property(self, prop, val):
            t.set_property(prop, val, f"[get_filesets {self.name}]")

        def add_file(self, path):
            t.cmd(f"add_files -fileset {self.name} [list [file normalize \"{path}\"]]")
            
    p = ZCU111Project(name)
    p.set_default_properties

    f_sources = Fileset("sources")
    f_sources.set_property("ip_repo_paths", "[file normalize \"../PiRadIP\"]")

    t.cmd("update_ip_catalog -rebuild")

    f_sources.set_property("dataflow_viewer_settings", "min_width=16")
    f_sources.set_property("top", wrapper_name)

    f_constraints = Fileset("constraints", "constrset")

    f_constraints.add_file(constraints_file)

    f_simulations = Fileset("simulations", "simset")

    f_simulations.set_property("top", wrapper_name)
    f_simulations.set_property("top_lib", "xil_defaultlib")

    

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
        t.cmd(f"get_ipdefs -all {ip}")

                
    bd = SDRv2_Capture(t, name)

    try:
        bd.validate()
    except Exception as e:
        print("Validation failed")
        pass
        
    bd.save()
    bd.close()
    
