from functools import cached_property
from pathlib import Path

from .build import BDBuildStep, GenerateBuildStep, WrapperBuildStep
from .build import SynthesizeBuildStep, OptimizationBuildStep
from .build import PlaceBuildStep, RouteBuildStep
from .build import WriteBitstreamBuildStep, XSABuildStep, DTBO


class NPM:
    def __init__(self, prj):
        self.prj = prj
        
        self.cmd(f"set_part {prj.board.fpga}")
        self.cmd(f"set_property TARGET_LANGUAGE Verilog [current_project]")
        self.cmd(f"set_property BOARD_PART {prj.board.part} [current_project]")
        self.cmd(f"set_property DEFAULT_LIB xil_defaultlib [current_project]")
        self.cmd(f"set_property IP_REPO_PATHS \"../PiRadIP\" [current_fileset]")
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
        WriteBitstreamBuildStep(self)
        XSABuildStep(self)
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

    def read_constraints(self):
        self.cmd(f"read_xdc {self.prj.constraints_path}")

    @property
    def top(self):
        return self.cmd("lindex [find_top] 0")        
