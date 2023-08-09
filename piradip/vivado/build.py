from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

from .synthesis import SynthesisMessageHandler

total_build_time = 0

class BuildStep:
    must_load = False
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.ready = False
        
        if self.predecessor_name is not None:
            self.predecessor = getattr(self.ctx, self.predecessor_name)
        else:
            self.predecessor = None
            
        setattr(self.ctx, self.name, self)


    def get_predecessor(self, name):
        if name == self.name:
            return self
        return self.predecessor.get_predecessor(name)
        
    def clean(self):
        self.predecessor.clean()
        self.do_clean()
        
    def __call__(self, **kwargs):
        assert self.predecessor is not None, "Root objects need to override __call__"

        # Check if predecessor is up-to-date
        self.predecessor(**kwargs)
                
        if not self.uptodate(**kwargs):
            print(f"Loading predecessor {self.predecessor.name}...")
            self.predecessor.load(**kwargs)            
                
            self.build_and_save(**kwargs)
            self.ready = True
        else:
            print(f"{self.name} is up-to-date...")
            if self.must_load:
                print(f"Loading {self.name}...")
                self.load(**kwargs)

    def load(self, **kwargs):
        if self.ready:
            return
        self.do_load(**kwargs)
        self.ready = True
        
    def do_load(self, **kwargs):
        self.build(**kwargs)
    
    def build_and_save(self, **kwargs):
        global total_build_time
        print(f"Executing build {self.name}")
        start_time = time.time()
        if self.build(**kwargs):
            self.save(**kwargs)
        self.ready = True
        build_time = time.time() - start_time
        total_build_time += build_time
        print(f"End build {self.name} Duration {build_time}")
    
    def save(self, **kwargs):
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
        
        if self.mtime() < self.predecessor.mtime():
            print(f"{self.name} is older than {self.predecessor.name}")
            return False

        return True
    
class CheckpointBuildStep(BuildStep):
    @property
    def checkpoint(self):
        return Path(f"{self.ctx.checkpoint_dir}/{self.name}.dcp")

    
    def do_load(self, **kwargs):
        print(f"Loading checkpoint for {self.name}...")
        self.cmd(f"open_checkpoint {self.checkpoint}")
        
    def save(self):
        print(f"Saving checkpoint for {self.name}...")
        self.cmd(f"write_checkpoint -force {self.checkpoint}", timeout=15*60)
    
    @property
    def exists(self):
        return self.checkpoint.exists()
            
    def mtime(self):
        try:
            return self.checkpoint.stat().st_mtime
        except:
            return time.time()

    def do_clean(self):
        self.checkpoint.unlink()

class FileBuildStep(BuildStep):
    @property
    def exists(self):
        return self.path.exists()

    def mtime(self):
        return self.path.stat().st_mtime
        
class BDBuildStep(FileBuildStep):
    name = "build_bd"
    predecessor_name = None

    def __call__(self):
        print(f"Reading block diagram {self.path}")
        self.cmd(f"read_bd {self.path}")
        self.cmd(f"update_compile_order -fileset sources_1")
        self.cmd(f"set_property SYNTH_CHECKPOINT_MODE NONE [get_files {self.path}]")
        
    @property
    def path(self):
        return Path(self.ctx.prj.bd_path)
        
        
class GenerateBuildStep(BuildStep):
    name = "generate"
    predecessor_name = "build_bd"

    def build(self, **kwargs):
        self.cmd(f"generate_target all [get_files {self.predecessor.path}]")
        self.cmd(f"export_ip_user_files -of_objects [get_files {self.predecessor.path}] -no_script -sync -force -quiet")
        
        output_root = self.predecessor.path.parent.parent
        
        self.cmd(f"export_simulation -of_objects [get_files {self.predecessor.path}]"
                 + f" -directory {output_root}/ip_user_files/sim_scripts"
                 + f" -ip_user_files_dir {output_root}/ip_user_files"
                 + f" -ipstatic_source_dir {output_root}/SDRv2.ip_user_files/ipstatic"
                 + f" -lib_map_path [list {{modelsim={output_root}/SDRv2.cache/compile_simlib/modelsim}}"
                 + f" {{questa={output_root}/SDRv2.cache/compile_simlib/questa}}"
                 + f" {{xcelium={output_root}/SDRv2.cache/compile_simlib/xcelium}}"
                 + f" {{vcs={output_root}/SDRv2.cache/compile_simlib/vcs}}"
                 + f" {{riviera={output_root}/SDRv2.cache/compile_simlib/riviera}}]"
                 + f" -use_ip_compiled_libs -force -quiet")
        self.cmd(f"read_bd {self.predecessor.path}")
                
    @property
    def bd_dir(self):
        return Path("block-design") / self.ctx.prj.project_name
    
    @property
    def exists(self):
        return (self.bd_dir / "ip").exists()
    
    def mtime(self):
        return self.predecessor.mtime()
    
class WrapperBuildStep(BuildStep):
    name = "make_and_read_wrapper"
    predecessor_name = "generate"
    pretty_name = "Make wrapper"
    
    def do_load(self, **kwargs):
        self.build(**kwargs)

    def build(self, **kwargs):
        print("Making and loading wrapper...")
        self.cmd(f"make_wrapper -files [get_files {self.ctx.prj.bd_path}] -top")
        self.cmd(f"read_verilog {self.ctx.prj.bd_wrapper}")
        for f in Path("sources").glob("*.v"):
            self.cmd(f"read_verilog {f}")
        self.cmd(f"update_compile_order -fileset sources_1")

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
        syn_msgs = SynthesisMessageHandler(self.ctx.vivado)

        top = self.cmd("lindex [find_top] 0")
        
        self.cmd(f"set_property top {top} [current_fileset]")
        self.cmd(f"set_property XPM_LIBRARIES {{XPM_CDC XPM_MEMORY XPM_FIFO}} [current_project]")
        self.cmd(f"synth_design -top {top} -flatten_hierarchy none", timeout=12*60*60)
        #self.cmd(f"synth_design -top {top}", timeout=12*60*60)


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
    must_load = True
    
    def build(self, **kwargs):
        self.cmd(f"route_design", timeout=12*60*60)
        self.cmd(f"report_timing_summary -file reports/routed_timing.rpt")
        return True
        
class XSABuildStep(FileBuildStep):
    name = "write_xsa"
    predecessor_name = RouteBuildStep.name
    pretty_name = "XSA"

    def load(self, **kwargs):
        print("No need to load: XSA up-to-date")
    
    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.xsa")

    def build(self, **kwargs):
        #self.cmd(f"read_bd {self.ctx.prj.bd_path}")
        self.cmd(f"set_property platform.name {self.ctx.prj.project_name} [current_project]")
        print(f"Writing XSA at {self.path}...")
        print(self.cmd(f"write_hw_platform -fixed -force -include_bit {self.path}", timeout=15*60))

    
class BitFileBuildStep(FileBuildStep):
    name = "write_bit"
    predecessor_name = XSABuildStep.name
    pretty_name = "Bitstream"

    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.bit")
    
    def build(self, **kwargs):
        os.system(f"unzip -o {self.predecessor.path} {self.path}")

        
class BinFileBuildStep(FileBuildStep):
    name = "write_bin"
    predecessor_name = BitFileBuildStep.name
    pretty_name = "BIN File"

    @property
    def bitfile_path(self):
        return Path(f"{self.ctx.prj.project_name}.bit")
    
    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.bit.bin")
    
    def build(self, **kwargs):
        def flip32(data):
            sl = struct.Struct('<I')
            sb = struct.Struct('>I')
            try:
                b = buffer(data)
            except NameError:
                # Python 3 does not have 'buffer'
                b = data
            d = bytearray(len(data))
            for offset in range(0, len(data), 4):
                sb.pack_into(d, offset, sl.unpack_from(b, offset)[0])
            return d

        short = struct.Struct('>H')
        ulong = struct.Struct('>I')
        
        bitfile = open(self.bitfile_path, 'rb')

        l = short.unpack(bitfile.read(2))[0]
        if l != 9:
            raise Exception("Missing <0009> header (0x%x), not a bit file" % l)
        bitfile.read(l)
        l = short.unpack(bitfile.read(2))[0]
        d = bitfile.read(l)
        if d != b'a':
            raise Exception("Missing <a> header, not a bit file")

        l = short.unpack(bitfile.read(2))[0]
        d = bitfile.read(l)
        print("Design name: %s" % d)

        # If bitstream is a partial bitstream, get some information from filename and header
        if b"PARTIAL=TRUE" in d:
            print("Partial bitstream")
            partial = True;

            # Get node_nr from filename (last (group of) digits)
            for i in range (len(args.bitfile) - 1, 0, -1):
                if args.bitfile[i].isdigit():
                    pos_end = i + 1
                    for j in range (i - 1, 0, -1):
                        if not args.bitfile[j].isdigit():
                            pos_start = j + 1
                            break
                        break
            if pos_end != 0 and pos_end != 0:
                node_nr = int(args.bitfile[pos_start:pos_end])
            else:
                node_nr = 0

            print("NodeID: %s" % node_nr)

            # Get 16 least significant bits of UserID in design name
            pos_start = d.find(b"UserID=")
            if pos_start != -1:
                pos_end = d.find(b";", pos_start)
                pos_start = pos_end - 4
                userid = int(d[pos_start:pos_end], 16)
                print("UserID: 0x%x" % userid)

        else:
            print("Full bitstream")
            partial = False
            node_nr = 0

        KEYNAMES = {b'b': "Partname", b'c': "Date", b'd': "Time"}

        while True:
            k = bitfile.read(1)
            if not k:
                bitfile.close()
                raise Exception("unexpected EOF")
            elif k == b'e':
                l = ulong.unpack(bitfile.read(4))[0]
                print("Found binary data: %s" % l)
                d = bitfile.read(l)
                if False:
                    print("Flipping data...")
                    d = flip32(d)
                # Open bin file
                binfile = open(self.path, 'wb')
                # Write header if it is a partial
                if partial:
                    binfile.write(struct.pack("B", 0))
                    binfile.write(struct.pack("B", node_nr))
                    binfile.write(struct.pack(">H", userid))
                # Write the converted bit-2-bin data
                print("Writing data...")
                binfile.write(d)
                binfile.close()
                break
            elif k in KEYNAMES:
                l = short.unpack(bitfile.read(2))[0]
                d = bitfile.read(l)
                print(KEYNAMES[k], d)
            else:
                print("Unexpected key: %s" % k)
                l = short.unpack(bitfile.read(2))[0]
                d = bitfile.read(l)

        bitfile.close()


class DTBO(FileBuildStep):
    name = "dtbo"
    predecessor_name = BinFileBuildStep.name
    pretty_name = "Device tree overlay"

    @property
    def path(self):
        return Path(f"{self.ctx.prj.project_name}.dtbo")

    @property
    def xsa_path(self):
        return self.get_predecessor(XSABuildStep.name).path
    
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
                    print(f"hsi::open_hw_design ../{self.xsa_path}", file=f)
                    print(f"hsi::set_repo_path device-tree-xlnx", file=f)
                    #print(f"hsi::get_cells")
                    #print(f"hsi create_dt_tree -verbose -dts_file pl.dtsi -dts_version /dts-v3/")
                    print(f"hsi create_sw_design device-tree -os device_tree -proc psu_cortexa53_0", file=f)
                    print(f"hsi set_property CONFIG.dt_overlay true [hsi::get_os]", file=f)
                    print(f"hsi generate_target -dir device-tree", file=f)

                assert os.system(f"xsct -eval 'source make_dtsi.tcl'") == 0
            else:
                s = f"hsi::open_hw_design ../{self.xsa_path}; "
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

        assert os.system(f"dtc -f -@ -O dtb -o {self.path} dtbo/fpga.dts") == 0
        
