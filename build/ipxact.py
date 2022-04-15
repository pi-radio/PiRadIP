from .piradip_build_base import *

from .structure import piradlib_files

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

    
library_rev=str(int(time.time()))

class IPXACTLibrary(IPXACTComponent2):
    def __init__(self, library_files):
        self.library_path = os.path.join(os.getcwd(), "library")
        self.library_files = library_files

        super(IPXACTLibrary, self).__init__(VLNV("pi-rad.io", "library", "PiRadIP", "1.0"), "Pi Radio IP Library")
        
        relpaths = [ os.path.relpath(i, self.library_path) for i in self.library_files ]

        self.synthesis_fs.file = [ ipxact_file(fn) for fn in relpaths ]
        
        self.simulation_fs.file = [ ipxact_file(fn) for fn in relpaths ]
                
        self.component.parameters = ipxact2009.Parameters()
        self.component.parameters.parameter = [
            ipxact2009.Parameter(name="Component_Name",
                                 value=ipxact2009.NameValuePairType.Value(
                                     value = "PiRadIP_v1_0",
                                     resolve="user",
                                     id="PARAM_VALUE.Component_Name",
                                     order=1
                                 )
            ) ]

        self.component.vendor_extensions = ipxact2009.VendorExtensions(
            any_element=CoreExtensions(
                taxonomies=CoreExtensions.Taxonomies( [
                    "/BaseIP",
                    "/Embedded_Processing/AXI_Infrastructure",
                    "/Memories_&_Storage_Elements"
                ] ),
                displayName="Pi Radio IP Library v1.0",
                hideInCatalogGUI=True,
                xpmLibraries=CoreExtensions.XPMLibraries(
                    [ CoreExtensions.XPMLibraries.XPMLibrary(i) for i in ["XPM_CDC", "XPM_FIFO", "XPM_MEMORY"]]
                ),
                vendorURL="https://pi-rad.io/",
                vendorDisplayName="Pi Radio Inc.",
                coreRevision=library_rev
            )
        )
        
class IPXACTModule(IPXACTComponent2):
    def __init__(self, module):
        self.module = module

        self.param_ids = {}
        self.model_param_ids = {}
        self.model_param_refs = {}
        
        super(IPXACTModule, self).__init__(VLNV("pi-rad.io", "library", self.module.ipxact_name, self.module.version), self.module.description)


        self.synthesis_fs.file = [ ipxact_file(self.module.rel_wrapper_verilog) ]
        self.simulation_fs.file = [ ipxact_file(self.module.rel_wrapper_verilog) ]
                
        
        self.component.file_sets.file_set.append(get_subcore_reference(library_rev))
        
        self.component.file_sets.file_set.append(ipxact2009.FileSet(name="bd_tcl_view_fileset", file=[ ipxact_file("bd/bd.tcl") ]))
        self.component.file_sets.file_set.append(ipxact2009.FileSet(name="xilinx_xpgui_view_fileset", file=[ ipxact_file("xgui/xgui.tcl") ]))

        self.component.model.views.view.append(
            ipxact2009.ViewType(name="bd_tcl",
                                display_name="Block Diagram",
                                env_identifier=":vivado.xilinx.com:block.diagram",
                                file_set_ref=ipxact2009.FileSetRef(local_name="bd_tcl_view_fileset")
            )
        )

        self.component.model.views.view.append(
            ipxact2009.ViewType(name="xilinx_xpgui",
                                display_name="UI Layout",
                                env_identifier=":vivado.xilinx.com:xgui.ui",
                                file_set_ref=ipxact2009.FileSetRef(local_name="xilinx_xpgui_view_fileset")
            )
        )

        
        self.component.vendor_extensions = ipxact2009.VendorExtensions(
            any_element=CoreExtensions(
                taxonomies=CoreExtensions.Taxonomies( [
                    "AXI_Peripheral"
                ] ),
                displayName=module.display_name,
                supportedFamilies=CoreExtensions.SupportedFamilies(
                    CoreExtensions.SupportedFamilies.Family(lifeCycle="Pre-Production", value="zynquplus")
                    ),
                
                vendorURL="https://pi-rad.io/",
                vendorDisplayName="Pi Radio Inc.",
                coreRevision=int(time.time())
            )
        )

        """
        self.component.vendor_extensions = ipxact2009.VendorExtensions(
            any_element=CoreExtensions(
                taxonomies=CoreExtensions.Taxonomies( [
                    "/BaseIP",
                    "/Embedded_Processing/AXI_Infrastructure",
                    "/Memories_&_Storage_Elements"
                ] ),
                displayName="Pi Radio IP Library v1.0",
                hideInCatalogGUI=True,
                xpmLibraries=CoreExtensions.XPMLibraries(
                    [ CoreExtensions.XPMLibraries.XPMLibrary(i) for i in ["XPM_CDC", "XPM_FIFO", "XPM_MEMORY"]]
                ),
                vendorURL="https://pi-rad.io/",
                vendorDisplayName="Pi Radio Inc.",
                coreRevision=library_rev
            )
        )
        """

        self.component.model.ports = ipxact2009.ModelType.Ports()
        self.component.parameters = ipxact2009.Parameters()
        self.component.model.model_parameters = ipxact2009.ModelType.ModelParameters()
        
    def generate_parameter(self, p):
        self.param_ids[p.name] = svsymbol(f"PARAM_VALUE.{p.name}")
        self.model_param_ids[p.name] = svsymbol(f"MODELPARAM_VALUE.{p.name}")

        self.model_param_refs[p.name] = svsymbol(f"spirit:decode(id('{self.model_param_ids[p.name]}'))")
        
        
        self.component.parameters.parameter.append(
            ipxact2009.Parameter(
                name=p.name,
                display_name=p.name,
                #description=p.description,
                value = ipxact2009.NameValuePairType.Value(
                    format="long",
                    resolve="user",
                    id=self.param_ids[p.name],
                    range_type=None,
                    value = str(p.default)
                    )
                )
            )

        self.component.model.model_parameters.model_parameter.append(
            ipxact2009.NameValueTypeType(
                name=p.name,
                display_name=p.name,
                #description=p.description,
                value = ipxact2009.NameValuePairType.Value(
                    format="long",
                    resolve="user",
                    id=self.model_param_ids[p.name],
                    range_type=None,
                    value=str(p.default)
                    )
                )
            )
        

    def generate_port(self, p):
        direction_map = { 'input': 'in', 'output': 'out' }

        print(f"Generating port {p.name} {p.datatype}")

        ipxact_wire = ipxact2009.PortWireType(
            direction=direction_map.get(p.direction, "DOOKIE"),
            all_logical_directions_allowed=None,
            wire_type_defs=ipxact2009.WireTypeDefs([ ipxact2009.WireTypeDef(
                type_name="wire",
                view_name_ref = [ self.synthesis_view_name, self.simulation_view_name ])
            ])
        )
            
        ipxact_port = ipxact2009.Port(
                name=p.name,
                wire=ipxact_wire
        )
        
        if p.datatype.vector:
            left = ipxact2009.Vector.Left(
                format="long",
                resolve=None,
                range_type=None
            )

            right = ipxact2009.Vector.Right(
                format="long",
                resolve=None,
                range_type=None
            )            
            
            if p.datatype.packed_range.left.const:
                left.value = str(p.datatype.packed_range.left)
            else:
                left.resolve="dependent"
                left.dependency = f"({p.datatype.packed_range.left.subst(self.model_param_refs)})"
                left.value="0"
                print(f"transform: {p.datatype.packed_range.left} => {str(left.dependency)}")
                

            if p.datatype.packed_range.right.const:
                right.value = str(p.datatype.packed_range.right)
            else:
                right.resolve="dependent"
                right.dependency = f"({p.datatype.packed_range.left.subst(self.model_param_refs)})"
                right.value="0"
                print(f"transform: {p.datatype.packed_range.right} => {str(right.dependency)}")
            
            ipxact_wire.vector = ipxact2009.Vector(
                left=left, right=right
            )

        self.component.model.ports.port.append(ipxact_port)
        

    def generate_interface(self, i):
        print(f"Generating interface {i.busname}")

        memory_map = None
        
        if i.ipxdesc.get('memoryMapped', False):
            if self.component.memory_maps is None:
                self.component.memory_maps = ipxact2009.MemoryMaps()
            
            memory_map = ipxact2009.MemoryMapType(
                name = i.busname,
                address_block = ipxact2009.AddressBlock(
                    name = i.busname + "_" + i.ipxdesc['mmtype'],
                    base_address = ipxact2009.BaseAddress(
                        format="long",
                        resolve="user",
                        range_type=None,
                        prompt=None,
                        value=0
                        ),
                    range = ipxact2009.AddressBlockType.Range(
                        format="long",
                        value="4096"
                        ),
                    width = ipxact2009.AddressBlockType.Width(
                        format="long",
                        value="32"
                    ),
                    usage = ipxact2009.UsageType("memory" if i.ipxdesc['mmtype'] == 'mem' else 'register'),
                    parameters = ipxact2009.Parameters()
                )
            )

            memory_map.address_block.parameters.parameter.append(
                ipxact2009.Parameter(
                    name="OFFSET_BASE_PARAM",
                    value=ipxact2009.NameValuePairType.Value(
                        id=f"ADDRBLOCKPARAM_VALUE.{i.busname}.{i.busname}_{i.ipxdesc['mmtype'].upper()}.OFFSET_BASE_PARAM",
                        value=f"C_{i.busname}_BASEADDR"
                        )
                    )
                )

            memory_map.address_block.parameters.parameter.append(
                ipxact2009.Parameter(
                    name="OFFSET_BASE_PARAM",
                    value=ipxact2009.NameValuePairType.Value(
                        id=f"ADDRBLOCKPARAM_VALUE.{i.busname}.{i.busname}_{i.ipxdesc['mmtype'].upper()}.OFFSET_HIGH_PARAM",
                        value=f"C_{i.busname}_HIGHADDR"
                        )
                    )
                )

            
            self.component.memory_maps.memory_map.append(memory_map)


        port_maps = ipxact2009.BusInterfaceType.PortMaps()

        for p in i.data_map:
            pm = port_maps.PortMap()
            pm.logical_port = pm.LogicalPort(name=i.ipxdesc["port_map"][i.data_map[p].name])
            pm.physical_port = pm.PhysicalPort(name=p)
            port_maps.port_map.append(pm)
            

        bif = ipxact2009.BusInterface(
            name = i.busname,
            bus_type = i.ipxdesc['busType'].library_ref,
            abstraction_type = i.ipxdesc['abstractionType'].library_ref,
            port_maps = port_maps
        )

        if i.modport.name == "SUBORDINATE":
            bif.slave = ipxact2009.BusInterfaceType.Slave()
            
            if memory_map:
                bif.slave.memory_map_ref = ipxact2009.MemoryMapRef(memory_map_ref=memory_map.name)
        elif i.modport.name == "MANAGER":
            bif.master = ipxact2009.BusInterfaceType.Master()

        
        self.component.bus_interfaces.bus_interface.append(bif)

        
        

    def generate(self):
        for p in self.module.params.values():
            self.generate_parameter(p)

        for p in self.module.ports.values():
            self.generate_port(p)

        if self.module.has_interfaces:
            self.component.bus_interfaces = ipxact2009.BusInterfaces()
            
            for i in self.module.interface_ports.values():
                if i.ipxdesc is not None:
                    self.generate_interface(i)

        
        
def build_libraries():
    library_path = os.path.join(os.getcwd(), "library")

    xml_path = os.path.join(library_path, "component.xml")
    
    input_times = [ os.path.getmtime(i) for i in piradlib_files ]
    
    input_times.append(os.path.getmtime("buildlib.py"))
    
    output_time = 0
    
    try:
        output_time = os.path.getmtime(xml_path)
    except FileNotFoundError:
        pass
    
    if False and all(output_time > i for i in input_times):
        INFO(f"Not rebuilding {xml_path} -- up to date")
        return

    l = IPXACTLibrary(piradlib_files)

    f = open(xml_path, "w")

    print(f"Writing library XML to {xml_path}...")
    l.export_ipxact(f)
    


