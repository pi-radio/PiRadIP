import os
from functools import cached_property
from pathlib import Path

from .build import BDBuildStep, GenerateBuildStep, WrapperBuildStep
from .build import SynthesizeBuildStep, OptimizationBuildStep
from .build import PlaceBuildStep, RouteBuildStep
from .build import XSABuildStep, BitFileBuildStep
from .build import BinFileBuildStep
from .build import DeviceTreeXilinx, DeviceTree, FPGA_DTS, DTBO


class NPM:
    def __init__(self, prj):
        self.prj = prj

        self.project_dir = Path.cwd()

        self.scripts_dir = self.project_dir / "scripts"
        
        self.post_synthesis_path = self.scripts_dir / "post_synth.tcl"
        
        piradip_root = Path(__file__).parent.parent.parent
        common_path = Path(os.path.commonpath((piradip_root, self.project_dir)))

        s = ""

        while not (self.project_dir/s).samefile(common_path):
            s += "../"

        modpath = Path(s) / piradip_root.relative_to(common_path)

        print(f"Relative IP repo path: {modpath}")
        
        self.cmd(f"set_part {prj.board.fpga}")
        self.cmd(f"set_property TARGET_LANGUAGE Verilog [current_project]")
        self.cmd(f"set_property BOARD_PART {prj.board.part} [current_project]")
        self.cmd(f"set_property DEFAULT_LIB xil_defaultlib [current_project]")
        self.cmd(f"set_property IP_REPO_PATHS [file normalize \"{modpath}\"] [current_fileset]")
        self.cmd(f"set_param messaging.defaultLimit 2000")

        self.checkpoint_dir = Path("checkpoints")
        
        Path("reports").mkdir(exist_ok=True)
        self.checkpoint_dir.mkdir(exist_ok=True)

        BDBuildStep(self)
        GenerateBuildStep(self)
        
        WrapperBuildStep(self)
        SynthesizeBuildStep(self)
        OptimizationBuildStep(self)
        PlaceBuildStep(self)
        RouteBuildStep(self)
        XSABuildStep(self)
        BitFileBuildStep(self)
        BinFileBuildStep(self)
        DeviceTreeXilinx(self)
        DeviceTree(self)
        FPGA_DTS(self)
        DTBO(self)
        
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

        self.cmd(f"open_bd_design [{self.prj.bd_path}]")
        
        for ip in self.ips:
            if not self.ip_locked(ip):
                continue
            
            details = self.cmd(f"get_property LOCK_DETAILS [get_ips {ip}]")
            print(f"IP {ip} is locked: {details}")    

            self.cmd(f"upgrade_ips [get_ips {ip}]")
            need_save = True

            self.cmd(f"export_ip_user_files -of_objects [get_ips {ip}]")
            
            if self.ip_locked(ip):
                details = self.cmd(f"get_property LOCK_DETAILS [get_ips {ip}]")
                locked.append((ip, details))

        if need_save:
            self.cmd("save_bd_design")
                
        return locked

    def load_bd(self, locked_ok=False):
        self.read_bd()

        if locked_ok:
            return
        
        locked = self.check_ips()

        if len(locked):
            raise RuntimeError(f"Some IP still locked: {locked}")

    def read_constraints(self):
        self.cmd(f"read_xdc {self.prj.constraints_path}")

    @property
    def top(self):
        return self.cmd("lindex [find_top] 0")        
