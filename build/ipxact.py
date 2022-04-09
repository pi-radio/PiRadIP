from .piradip_build_base import *

from .ipxact_base import *
from .ipxact_bus import *

class IPXACTChoiceList:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    @property
    def xml(self):
        choice = S.choice(S.name(self.name))
        for v in self.values:
            choice.append(S.enumeration(v))
        return choice

interrupt_sensitivity_list = IPXACTChoiceList("choice_list_99a1d2b8", [ 'LEVEL_HIGH', 'LEVEL_LOW', 'EDGE_RISING', 'EDGE_FALLING' ] )
polarity_list = IPXACTChoiceList("choice_list_9d8b0d81", [ 'ACTIVE_HIGH', 'ACTIVE_LOW' ] )

direction_map = { 'input': 'in', 'output': 'out' }

class IPXACTModule():
    def __init__(self, module):
        self.module = module

        self.bus_interfaces = S.busInterfaces()
        self.memory_maps = S.memoryMaps()

        self.views = S.views()
        self.ports = S.ports()
        
        self.model = S.model(self.views, self.ports)
        self.choices = S.choices()
        self.file_sets = S.fileSets()
        self.parameters = S.parameters()
        self.xilinx_core_ext = X.coreExtensions()
        #self.xilinx_packaging = X.packagingInfo()
        
        self.component = S.component(
            S.vendor("pi-rad.io"),
            S.library("piradip"),
            S.name(self.module.ipxact_name),
            S.version(self.module.version),
            self.bus_interfaces,
            self.memory_maps,
            self.model,
            self.choices,
            self.file_sets,
            S.description(self.module.description),
            self.parameters,
            S.vendorExtensions(self.xilinx_core_ext)
        )

        self.choices.append(interrupt_sensitivity_list.xml)
        self.choices.append(polarity_list.xml)
        
        comp_mode = X.mode();
        comp_mode.attrib[f"{{{NS_XILINX}}}name"] = "copy_mode"
        comp_ref = X.componentRef(comp_mode)
        
        comp_ref.attrib[f"{{{NS_XILINX}}}vendor"] = "pi-rad.io"
        comp_ref.attrib[f"{{{NS_XILINX}}}library"] = "PiRadIP"
        comp_ref.attrib[f"{{{NS_XILINX}}}name"] = "PiRadIP"
        comp_ref.attrib[f"{{{NS_XILINX}}}version"] = PiRadIP_Version

        sub_core_ref_fs_name = "xilinx_anylanguagesynthesis_pi_rad_io_PiRadIP_PiRadIP_1_0__ref_view_fileset"
        synth_ref_fs_name = "xilinx_anylanguagesynthesis_view_fileset"
        
        sub_core_ref = S.fileSet(
                S.name(sub_core_ref_fs_name),
                S.vendorExtensions(
                    X.subCoreRef(comp_ref)
                    )
                )

        synthesis_fileset = S.fileSet(
            S.name(synth_ref_fs_name),
            S.file(
                S.name("hdl/"+self.module.wrapper_file_name),
                S.fileType("systemVerilogSource")
            )
        )

        self.file_sets.append(synthesis_fileset)
        self.file_sets.append(sub_core_ref)


        family = X.family('zynquplus')
        family.attrib[f"{{{NS_XILINX}}}lifeCycle"] = "Pre-Production"

        self.xilinx_core_ext.append(X.supportedFamilies(family))

        self.xilinx_core_ext.append(X.taxonomies(X.taxonomy("AXI_Peripheral")))

        self.xilinx_core_ext.append(X.displayName(self.module.display_name))

        self.views.append(
            S.view(
                S.name("xilinx_anylanguagesynthesis"),
                S.displayName("Synthesis"),
                S.envIdentifier(),
                S.modelName(),
                S.fileSetRef(S.localName(sub_core_ref_fs_name)),
                S.fileSetRef(S.localName(synth_ref_fs_name))
                # S.parameters -- but no checksum??
                # S.parameters(S.parameter(S.name("viewChecksum"), S.value("XXXXXX")))
            )
            )
            
        

    def export_ipxact(self, f):
        print(etree.tostring(self.component, pretty_print=True).decode(), file=f)


    def add_port(self, name, direction, typename):
        
        print(f"Add port {name}")

        self.ports.append(S.port(S.name(name),
                      S.wire(
                          S.direction(direction_map[direction]),
                          S.wireTypeDefs(
                              S.wireTypeDef(
                                  S.typeName("wire"),
                                  S.viewNameRef("xilinx_anylanguagesynthesis"),
                                  S.viewNameRef("xilinx_verilogbehavioralsimulation")
                                  )
                              )
                          )
                      ));
        


"""
      <spirit:port>
        <spirit:name>miso</spirit:name>
        <spirit:wire>
          <spirit:direction>in</spirit:direction>
          <spirit:wireTypeDefs>
            <spirit:wireTypeDef>
              <spirit:typeName>wire</spirit:typeName>
              <spirit:viewNameRef>xilinx_anylanguagesynthesis</spirit:viewNameRef>
              <spirit:viewNameRef>xilinx_verilogbehavioralsimulation</spirit:viewNameRef>
            </spirit:wireTypeDef>
          </spirit:wireTypeDefs>
        </spirit:wire>
      </spirit:port>
"""
