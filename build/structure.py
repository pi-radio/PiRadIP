from .piradip_build_base import *

import os
from pathlib import PurePath, Path

from dataclasses import dataclass, field
from typing import Dict, List, Optional

build_root = Path(__file__).parent.parent.absolute()

INFO(f"Build root: {build_root}")

piradlib_files = []

interface_map = {}

module_map = {}

library_map = {}

@dataclass
class VLNV:
    vendor: str
    library: str
    name: str
    version: str
    
    @property
    def vlnv(self):
        return f"{self.vendor}:{self.library}:{self.name}:{self.version}"
    
    @property
    def library_ref(self):
        return ipxact2009.LibraryRefType(vendor = self.vendor,
                                         library = self.library,
                                         name = self.name,
                                         version = self.version)


@dataclass
class ParameterDesc:
    name: str
    description: str
    allowed_values: Optional[List[int]] = field(default_factory=list)
    prefix: str = ""
    
@dataclass
class IPXParameterDesc(ParameterDesc):
    usage: str = "all"
    ipxact_id: str = "bogus"
    order: int = 0
    default_value: str = "bogus"
    value_format: str = "long"
    value_source: str = "constant"
    
@dataclass
class IPXClock:
    name: str

@dataclass
class IPXReset:
    name: str
    polarity: str
    
@dataclass
class IPXDesc:
    busType: VLNV
    abstractionType: VLNV
    ports: List[str]
    port_map: Dict[str, str]
    clock: IPXClock
    reset: IPXReset
    memoryMapped: bool = False
    mmtype: str = ""
    xilinxParameters: Optional[List[IPXParameterDesc]] = field(default_factory=list)

@dataclass
class InterfaceDesc:
    name: str
    file: str
    parameters: List[ParameterDesc]
    ipxdesc: Optional[IPXDesc] = None                 

    def __post_init__(self):
        self.param_map = { p.name: p  for p in self.parameters }
        interface_map[self.name] = self
        

@dataclass
class ModuleDesc:
    name: str
    file: str
    wrapper_name: str
    description: str
    display_name: str
    version: str
    ipxact_name: str
    parameters: List[ParameterDesc] = field(default_factory=list)

    def __post_init__(self):
        self.param_map = { p.name: p  for p in self.parameters }
        module_map[self.name] = self

    @property
    def wrapper_file_name(self):
        return f"{self.wrapper_name}_{self.version}.sv"

    @property
    def wrapper_path(self):
        return PurePath(self.wrapper_name)

    @property
    def wrapper_verilog_path(self):
        return self.wrapper_path.joinpath(self.wrapper_verilog_relpath)

    @property
    def wrapper_verilog_relpath(self):
        return PurePath('hdl').joinpath(self.wrapper_file_name)
    
    @property
    def wrapper_xgui_relpath(self):
        return PurePath('xgui').joinpath("xgui.tcl")

    @property
    def wrapper_xgui_path(self):
        return self.wrapper_path.joinpath(self.wrapper_xgui_relpath)

    @property
    def wrapper_xml_path(self):
        return self.wrapper_path.joinpath("component.xml")

    @property
    def wrapper_bd_tcl_path(self):
        return self.wrapper_path.joinpath("bd/bd.tcl")

    
    @property
    def ipx_generate_script(self):
        return f"generate_{self.wrapper_name}.tcl"
    
@dataclass
class Library:
    name: str
    files: List[str]

    def __post_init__(self):
        library_map[self.name] = self

    
def add_library_file(file):
    piradlib_files.append(file)
