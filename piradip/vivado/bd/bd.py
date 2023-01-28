from functools import cached_property

from piradip.vivado.obj import VivadoObj
from piradip.vivado.property import VivadoProperty

from .obj import BDObj
from .connector import BDConnector
from .port import BDIntfPort, BDPort
from .memory_map import BDMemoryMapper


class BDFile(VivadoObj):
    def __init__(self, parent, filename):
        super().__init__(parent, filename)

    @property
    def obj(self):
        return f"[get_files {self.name}]"

class BD(BDConnector, BDObj):
    hier = True
    root = True
    
    extern_intf_type = BDIntfPort
    extern_pin_type = BDPort

    def __init__(self, project, name):
        super().__init__(project, name)
        self.cmd(f"create_bd_design -dir block-design -verbose {name}")
        
        self._current = self
        self.name = name
        self.intf_ports = dict()
        self.ports = dict()
        self._filename = self.get_property("FILE_NAME")
        self._output_dir = self.get_property("BD_OUTPUT_DIR")

        self.port_phys = dict()
        self.phys_map = dict()
        
        self.logs.mkdir(exist_ok=True)
        
    @property
    def logs(self):
        return self.parent.logs / "bd"
        
    @property
    def filename(self):
        return self._filename

    @property
    def output_dir(self):
        return self._output_dir
    
    @cached_property
    def file(self):
        return BDFile(self, self.filename)
        
    @property
    def obj(self):
        return "[current_bd_design]"
        
    @property
    def path(self):
        return "/"

    @property
    def path(self):
        return "/"

    @property
    def wrapper_name(self):
        return self.name + "_wrapper"
        
    def get_current(self):
        return self._current
        
    def set_current(self, cell):
        if self._current != cell:
            self._current = cell
            if cell is not None:
                self.cmd(f"current_bd_instance {cell.path}")
                
    def validate(self):
        self.cmd("validate_bd_design")
                
    def save(self):
        self.cmd("save_bd_design")

    def close(self):
        self.cmd(f"close_bd_design {self.name}")

    def wrap(self):
        self.file.set_property("REGISTERED_WITH_MANAGER", "1")
        self.file.set_property("SYNTH_CHECKPOINT_MODE", "Hierarchical")
        
        if int(self.file.get_property("IS_LOCKED")):
            print("Ugh, need to import wrapper somehow")
            sys.exit(0)
        else:
            self.cmd(f"add_files -norecurse -fileset {self.parent.src_fileset.name} [make_wrapper -fileset {self.parent.src_fileset.name} -files {self.file.obj} -top]")
        self.parent.src_fileset.set_property("top", self.wrapper_name)
        self.parent.simulation_fileset.set_property("top", self.wrapper_name)

        for k, v in self.port_phys.items():
            print(f"Mapping {k} to {v[0]} IO: {v[1]}")

            print(f"set_property PACKAGE_PIN {v[0]} [get_ports {k}]", file=self.parent.constraints_file)
            print(f"set_property IOSTANDARD {v[1]} [get_ports {k}]", file=self.parent.constraints_file)

            
            
    def generate(self):
        self.cmd(f"generate_target all {self.file.obj}")
        
        
    def assign_addresses(self, root=None):
        if root is None:
            l = list(filter(lambda x: x.vlnv == "xilinx.com:ip:zynq_ultra_ps_e:3.4", self.ip_cells))
            assert len(l) == 1
            root = l[0]

        self.mmap = BDMemoryMapper(self, root)
