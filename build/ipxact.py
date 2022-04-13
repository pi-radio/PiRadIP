from .piradip_build_base import *

from .structure import piradlib_files

from .ipxact_base import *
from .ipxact_node import *
from .ipxact_bus import *
from .ipxact_collection import *
from .ipxact_component import *

import lxml.etree
import io
import datetime
import os
import os.path


class IPXACTLibrary():
    def __init__(self, library_files):
        library_name = "PiRadIP"
        library_version = "1.0"
        library_description = "Pi Radio IP Library"

        self.library_path = os.path.join(os.getcwd(), "library")
        self.library_files = library_files
        
        relpaths = [ os.path.relpath(self.library_path, i) for i in self.library_files ]

        input_times = [ os.path.getmtime(i) for i in self.library_files ]

        input_times.append(os.path.getmtime("buildlib.py"))

        output_time = 0
        
        try:
            output_time = os.path.getmtime(self.xml_path)
        except FileNotFoundError:
            pass
            
        if all(output_time > i for i in input_times):
            INFO(f"Not rebuilding {self.xml_path} -- up to date")
        
        synthesis_fileset_name = "xilinx_anylanguagesynthesis_view_fileset"
        simulation_fileset_name = "xilinx_anylanguagebehavioralsimulation_view_fileset"
        
        self.synthesis_view = S.view(
            S.name("xilinx_anylanguagesynthesis"),
            S.displayName("Synthesis"),
            S.envIdentifier(":vivado.xilinx.com:synthesis"),
            S.language("SystemVerilog"),
            S.fileSetRef(synthesis_fileset_name)
        )

        self.simulation_view = S.view(
            S.name("xilinx_anylanguagebehavioralsimulation"),
            S.displayName("Simulation"),
            S.envIdentifier(":vivado.xilinx.com:simulation"),
            S.language("SystemVerilog"),
            S.fileSetRef(simulation_fileset_name)
        )
        
        self.model = S.model(self.synthesis_view,
                             self.simulation_view)

        self.synthesis_fileset = S.fileSet(
            S.name(synthesis_fileset_name)
            )

        self.simulation_fileset = S.fileSet(
            S.name(simulation_fileset_name)
            )        
        
        self.file_sets = S.fileSets(self.synthesis_fileset,
                                    self.simulation_fileset)

        for filename in library_files:
            relative_filename = os.path.relpath(filename, self.library_path)
            
            self.synthesis_fileset.append(
                S.file(
                    S.name(relative_filename),
                    S.fileType("systemVerilogSource"),
                    S.logicalName("library")
                )
            )
            
            self.simulation_fileset.append(
                S.file(
                    S.name(relative_filename),
                    S.fileType("systemVerilogSource"),
                    S.logicalName("library")
                )
            )

        
        self.parameters = S.parameters()

        self.xilinx_core_ext = X.coreExtensions(
            X.taxonomies(
                X.taxonomy("/BaseIP"),
                X.taxonomy("/Embedded_Processing/AXI_Infrastructure"),
                X.taxonomy("/Memories_&_Storage_Elements"),
            ),
            X.displayName("PiRadIP_v1_0"),
            X.hideInCatalogGUI("true"),
            X.definitionSource("package_project"),
            X.xpmLibraries(
                X.xpmLibrary("XPM_CDC"),
                X.xpmLibrary("XPM_FIFO"),
                X.xmpLibrary("XPM_MEMORY")
                ),
            X.vendorDisplayName("Pi Radio Inc."),
            X.vendorURL("https://pi-rad.io/"),
            X.coreRevision("1"),
            X.upgrades(X.canUpgradeFrom("pi-rad.io:ip:library:1.0")),
            X.coreCreationDateTime(datetime.datetime.utcnow().strftime("%Y-%M-%jT%H:%M:%SZ"))
            )
        
        self.component = S.component(
            S.vendor("pi-rad.io"),
            S.library("piradip"),
            S.name(library_name),
            S.version(library_version),
            self.model,
            self.file_sets,
            S.description(library_description),
            self.parameters,
            S.vendorExtensions(self.xilinx_core_ext)
            )

    @property
    def xml_path(self):
        return os.path.join(self.library_path, "component.xml")
        
    def export_ipxact(self, f):
        print(lxml.etree.tostring(self.component, encoding='UTF-8', pretty_print=True, xml_declaration=True).decode(), file=f)

        
def build_libraries():
    l = IPXACTLibrary(piradlib_files)

    f = open(l.xml_path, "w")
    
    l.export_ipxact(f)
    

    

class IPXACTModule(IPXACTComponent):
    def __init__(self, module):
        self.module = module

        super(IPXACTModule, self).__init__(None, "pi-rad.io", "piradip",
                                           self.module.ipxact_name, self.module.version)

        #self.xilinx_packaging = X.packagingInfo()


        #self.choices.append(interrupt_sensitivity_list.xml)
        #self.choices.append(polarity_list.xml)        

        self.file_sets.add_subclass(IPXACTSubCoreReference, "xilinx_anylanguagesynthesis_pi_rad_io_PiRadIP_PiRadIP_1_0__ref_view_fileset")
        self.file_sets.add("xilinx_anylanguagesynthesis_view_fileset",
                           files=[
                               {
                                   'file': self.module.wrapper_verilog.relative_to(self.module.wrapper_path),
                                   'type': 'systemVerilogSource'
                               }
                           ]
        )
        

        self.file_sets.add("bd_tcl_view_fileset",
                           files =[
                               {
                                   'file': self.module.bd_tcl.relative_to(self.module.wrapper_path),
                                   'type': 'tclSource'
                               }
                           ]
        )

        self.file_sets.add("xilinx_xpgui_view_fileset",
                           files =[
                               {
                                   'file': self.module.xgui_tcl.relative_to(self.module.wrapper_path),
                                   'type': 'tclSource',
                                   'userFileTypes': [ 'XGUI_VERSION_2' ]
                               }
                           ]
        )


        

        family = X.family('zynquplus')
        family.attrib[f"{{{NS_XILINX}}}lifeCycle"] = "Pre-Production"

        self.xilinx_core_ext = X.coreExtensions()
        self.xilinx_core_ext.append(X.supportedFamilies(family))

        self.xilinx_core_ext.append(X.taxonomies(X.taxonomy("AXI_Peripheral")))

        self.xilinx_core_ext.append(X.displayName(self.module.display_name))

        view = self.model.views.add("xilinx_anylanguagesynthesis", "Synthesis")

        view = self.model.views.add("bd_tcl", "Block Diagram", envIdentifier=":vivado.xilinx.com:block_diagram")

        

    def attr(self, s):
        return f"{{{NS_SPIRIT}}}{s}"
        

    def export_ipxact(self, f):
        self.resolve()
        print(lxml.etree.tostring(self.node,  encoding='UTF-8', pretty_print=True, xml_declaration=True).decode(), file=f)
        
        

