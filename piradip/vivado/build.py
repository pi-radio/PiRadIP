from pathlib import Path
import time
import sys
import os
import pexpect
from multiprocessing import Process

from .synthesis import SynthesisMessageHandler

class BuildStep:
    def __init__(self, ctx):
        self.ctx = ctx
        
        if self.predecessor_name is not None:
            self.predecessor = getattr(self.ctx, self.predecessor_name)
        else:
            self.predecessor = None
            
        setattr(self.ctx, self.name, self)

    def __call__(self, **kwargs):
        if self.uptodate(**kwargs):
            return

        if self.predecessor is not None:
            if self.predecessor.uptodate(**kwargs):
                self.predecessor.load()
            else:
                self.predecessor(**kwargs)
                
        if self.build(**kwargs):
            self.save(**kwargs)

    def load(self):
        pass

    def save(self):
        pass
            
    def cmd(self, t, **kwargs):
        return self.ctx.cmd(t, **kwargs)

    def uptodate(self, **kwargs):
        print(f"Checking if {self.name} is up-to-date...")
        if kwargs.get("force", False):
            print(f"Forcing rebuild of {self.name}")
            return False
        
        if not self.exists:
            print(f"{self.name} does not exist")
            return False

        if self.predecessor is None:
            return True
        
        if not self.predecessor.uptodate(**kwargs):
            print(f"{self.predecessor.name} is not up to date")
            return False

        if self.mtime() < self.predecessor.mtime():
            print(f"{self.name} is older than {self.predecessor.name}")
            return False

        return True
    
class BDBuildStep(BuildStep):
    name = "build_bd"
    predecessor_name = None

    def __call__(self, **kwargs):        
        pass

    @property
    def path(self):
        return Path(self.ctx.prj.bd_path)
    
    @property
    def exists(self):
        return self.path.exists()
    
    def mtime(self):
        return self.path.stat().st_mtime

class CheckpointBuildStep(BuildStep):
    @property
    def checkpoint(self):
        return Path(f"{self.ctx.checkpoint_dir}/{self.name}.dcp")

    def load(self):
        print(f"Loading checkpoint for {self.name}...")
        self.cmd(f"open_checkpoint {self.checkpoint}")
        
    def save(self):
        print(f"Saving checkpoint for {self.name}...")
        self.cmd(f"write_checkpoint -force {self.checkpoint}")
    
    @property
    def exists(self):
        return self.checkpoint.exists()
            
    def mtime(self):
        try:
            return self.checkpoint.stat().st_mtime
        except:
            return time.time()
        
class GenerateBuildStep(BuildStep):
    name = "generate"
    predecessor_name = "build_bd"

    def __call__(self, **kwargs):
        self.cmd(f"read_bd {self.ctx.prj.bd_path}")
        
        self.cmd(f"set_property synth_checkpoint_mode None [get_files {self.ctx.prj.bd_path}]")
        self.cmd(f"generate_target all [get_files {self.ctx.prj.bd_path}]")

    @property
    def bd_dir(self):
        return Path("block-design") / self.ctx.prj.project_name

    @property
    def exists(self):
        return (self.bd_dir / "ip").exists()
    
    def mtime(self):
        self()
        return self.predecessor.mtime()

    
        bd_files = list((self.bd_dir / "ip").rglob("*"))
        
        bd_mtime = 0
        max_file = None

        for f in bd_files:
            t = f.stat().st_mtime
            if t > bd_mtime:
                bd_mtime = t
                max_file = f

        print(f"Max file: {max_file}")

        print(list(sorted(bd_files, key=lambda f: f.stat().st_mtime))[-10:])

        return bd_mtime
    
class WrapperBuildStep(BuildStep):
    name = "make_and_read_wrapper"
    predecessor_name = "generate"
    pretty_name = "Make wrapper"
    
    def __call__(self, **kwargs):
        self.ctx.generate()
        self.cmd(f"make_wrapper -files [get_files {self.ctx.prj.bd_path}] -top")
        self.cmd(f"read_verilog {self.ctx.prj.bd_wrapper}")
        self.cmd(f"update_compile_order -fileset sources_1")
        return True

    @property
    def wrapper(self):
        return Path(self.ctx.prj.bd_wrapper)

    
    @property
    def exists(self):
        print(self.wrapper)
        return self.wrapper.exists()
        
    def mtime(self):
        return self.wrapper.stat().st_mtime
        
    
class SynthesizeBuildStep(CheckpointBuildStep):
    name = "synthesize"
    predecessor_name = WrapperBuildStep.name
    pretty_name = "Synthesis"
    
    def build(self, **kwargs):
        sys.exit(0)
        syn_msgs = SynthesisMessageHandler(self.ctx.vivado)

        top = self.cmd("lindex [find_top] 0")
        
        self.cmd(f"set_property top {top} [current_fileset]")
        self.cmd(f"set_property XPM_LIBRARIES {{XPM_CDC XPM_MEMORY XPM_FIFO}} [current_project]")
        self.cmd(f"synth_design -top {top} -flatten_hierarchy none", timeout=12*60*60)

        syn_msgs.show_locations()
        
        self.cmd(f"report_timing_summary -file reports/synthesis_timing.rpt")

        # Hmm, batch this up?
        syn_msgs.end_report()
        
        return True

class OptimizationBuildStep(CheckpointBuildStep):
    name = "optimize"
    predecessor_name = SynthesizeBuildStep.name
    pretty_name = "Logical optimization"

    def build(self, **kwargs):
        self.cmd(f"opt_design", timeout=12*60*60)

        self.cmd(f"report_timing_summary -file reports/opt_timing.rpt")
        return True
        
class PlaceBuildStep(CheckpointBuildStep):
    name = "place"
    predecessor_name = OptimizationBuildStep.name
    pretty_name = "Placement"

    def build(self, **kwargs):
        self.cmd(f"read_xdc constraints/{self.ctx.prj.project_name}.xdc")

        print("Exported ports:")
        for p in self.cmd("get_ports").split():
            loc = self.cmd(f"get_property PACKAGE_PIN [get_ports {p}]")
            std = self.cmd(f"get_property IOSTANDARD [get_ports {p}]")
            print(f"  {p}: {loc} {std}")
        
        
        self.cmd(f"place_design", timeout=12*60*60)
        self.cmd(f"phys_opt_design", timeout=12*60*60)

        self.cmd(f"report_timing_summary -file reports/placed_timing.rpt")
        return True
        
class RouteBuildStep(CheckpointBuildStep):
    name = "route"
    predecessor_name = PlaceBuildStep.name
    pretty_name = "Routing"

    def build(self, **kwargs):
        self.cmd(f"route_design", timeout=12*60*60)
        self.cmd(f"report_timing_summary -file reports/routed_timing.rpt")
        return True

class FileBuildStep(BuildStep):
    @property
    def exists(self):
        return self.path.exists()

    def mtime(self):
        return self.path.stat().st_mtime
    
class WriteBitstreamBuildStep(FileBuildStep):
    name = "write_bitstream"
    predecessor_name = RouteBuildStep.name
    pretty_name = "Bitstream"

    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.bit")
    
    def build(self, **kwargs):
        self.cmd(f"write_bitstream -force -bin {self.path}")
        os.system(f"mv {self.ctx.prj.project_name}.bin {self.ctx.prj.project_name}.bit.bin")
        
class XSABuildStep(FileBuildStep):
    name = "write_xsa"
    predecessor_name = RouteBuildStep.name
    pretty_name = "XSA"
        
    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.xsa")

    def build(self, **kwargs):
        #self.cmd(f"read_bd {self.ctx.prj.bd_path}")
        self.cmd(f"set_property platform.name {self.ctx.prj.project_name} [current_project]")
        print(f"Writing XSA at {self.path}...")
        print(self.cmd(f"write_hw_platform -fixed -force -include_bit {self.path}"))

class XSCT:
    def __init__(self):
        self.p = pexpect.spawnu("xsct -norlwrap -interactive", env = os.environ | { 'TERM': 'dumb' })
        self.p.logfile = sys.stdout
        self.p.expect("xsct% ")
        self.p.setecho(False)
        print(f"Before {self.p.before}")
        
    def cmd(self, l):
        self.p.sendline(f"{l}")
        while self.p.expect(["xsct% ", "invalid command name"]) != 0:
            print(f"Non-zero: {self.p.before}")
        print(f"Before {self.p.before}")
        time.sleep(2)
        #sys.stdout.flush()
        
class DTBO(FileBuildStep):
    name = "dtbo"
    predecessor_name = "write_xsa"
    pretty_name = "Device tree overlay"

    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.dtbo")

    
    def build(self, **kwargs):
        dtbo_root = Path("dtbo")
        xilinx_rel="2022.2"
        
        dtbo_root.mkdir(exist_ok=True)

        pwd = os.getcwd()
        
        try:
            os.chdir(dtbo_root)

            if not Path("device-tree-xlnx").exists():
                os.system(f"git clone https://github.com/Xilinx/device-tree-xlnx && cd device-tree-xlnx && git checkout xlnx_rel_v{xilinx_rel}")

            if False:
                # don't try to use expect with xsct.  It is broken, broken java of the devil which breaks everything
                with open("make_dtsi.tcl", "w") as f:                
                    print(f"hsi::open_hw_design ../{self.predecessor.path}", file=f)
                    print(f"hsi::set_repo_path device-tree-xlnx", file=f)
                    #print(f"hsi::get_cells")
                    #print(f"hsi create_dt_tree -verbose -dts_file pl.dtsi -dts_version /dts-v3/")
                    print(f"hsi create_sw_design device-tree -os device_tree -proc psu_cortexa53_0", file=f)
                    print(f"hsi set_property CONFIG.dt_overlay true [hsi::get_os]", file=f)
                    print(f"hsi generate_target -dir device-tree", file=f)

                assert os.system(f"xsct -eval 'source make_dtsi.tcl'") == 0
            else:
                s = f"hsi::open_hw_design ../{self.predecessor.path}; "
                s += f"hsi::set_repo_path device-tree-xlnx; "
                s += f"hsi create_sw_design device-tree -os device_tree -proc psu_cortexa53_0; "
                s += f"hsi set_property CONFIG.dt_overlay true [hsi::get_os]; "
                s += f"hsi generate_target -dir device-tree;"

                assert os.system(f"xsct -eval '{s}'") == 0

                
                
            assert os.system(f"cp device-tree/pl.dtsi fpga.dts") == 0

            if Path("../fpga.dtsi").exists():
                assert os.system(f"cat ../fpga.dtsi >> fpga.dts") == 0
        finally:
            os.chdir(pwd)

        assert os.system(f"dtc -@ -O dtb -o {self.path} dtbo/fpga.dts") == 0
        
