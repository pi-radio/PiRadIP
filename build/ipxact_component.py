from .ipxact_base import *
from .ipxact_node import *
from .ipxact_bus import *

class IPXACTComponent2():
    synthesis_view_name="xilinx_anylanguagesynthesis"
    simulation_view_name="xilinx_anylanguagebehavioralsimulation"
    
    def __init__(self, vlnv, description):
        self.synthesis_fs = ipxact2009.FileSet()
        self.synthesis_fs.name = "xilinx_anylanguagesynthesis_view_fileset"

        self.simulation_fs = ipxact2009.FileSet()
        self.simulation_fs.name = "xilinx_anylanguagebehavioralsimulation_view_fileset"

        synthesis_view = ipxact2009.ViewType(name=self.synthesis_view_name,
                                             display_name = "Synthesis",
                                             env_identifier = ":vivado.xilinx.com:synthesis",
                                             language = "SystemVerilog",
                                             file_set_ref = ipxact2009.FileSetRef(local_name="xilinx_anylanguagesynthesis_view_fileset"))

        simulation_view = ipxact2009.ViewType(name=self.simulation_view_name,
                                             display_name = "Simulation",
                                             env_identifier = ":vivado.xilinx.com:simulation",
                                             language = "SystemVerilog",
                                             file_set_ref = ipxact2009.FileSetRef(local_name="xilinx_anylanguagebehavioralsimulation_view_fileset"))

        
        self.component = ipxact2009.Component(
            vendor = vlnv.vendor,
            library = vlnv.library,
            name = vlnv.name,
            version = vlnv.version,
            description = description,
            file_sets = ipxact2009.FileSets([ self.synthesis_fs, self.simulation_fs ]),
            model = ipxact2009.Model(
                views = ipxact2009.Model.Views([ synthesis_view, simulation_view ])
            )
        )

    def export_ipxact(self):
        INFO(f"Writing library XML to {self.desc.xml_path}...")
        f = self.xml_file("w")
        config = SerializerConfig(pretty_print=True)
        serializer = XmlSerializer(config=config)
        print(serializer.render(self.component, ns_map=ns_map), file=f)

        #print(lxml.etree.tostring(self.component, encoding='UTF-8', pretty_print=True, xml_declaration=True).decode(), file=f)

        
        
