from .ipxact_base import *

class ipxact_bus_inst:
    def __init__(self, bus, name):
        self.bus = bus
        self.name = name
        
class ipxact_bus:
    def __init__(self, bus_type, abstraction_type, logical_ports=[], parameters=[]):
        self.bus_type = bus_type
        self.abstraction_type = abstraction_type
        self.logical_ports = logical_ports
        self.parameters = parameters


    def generate(self, port_mapping, slave=True, memory_map=None):
        
        n = S.busInterface()

        if memory_map:
            mm_ref = S.memoryMapRef();
            mm_ref.attrib[f"{{{NS_SPIRIT}}}{memory_map}"]
            if slave:
                n.append(S.slave(mm_ref))
            else:
                m.append(S.master(mm_ref))
                
        n.append(self.generate_port_maps, port_mapping)

    def generate_port_maps(self, port_mapping):
        pms = S.portMaps()

        for lp in self.logical_ports:
            pm = S.portMap(
                S.logicalPort(S.name(lp)),
                S.physicalPort(S.name(port_mapping(lp)))
                )
            pms.append(pm)

        return pms
        

XILINX_RESET = ipxact_bus(VLNV(name="reset"), VLNV(name="reset_rtl"), logical_ports=[ "RST" ], parameters=["POLARITY"])
XILINX_CLOCK = ipxact_bus(VLNV(name="clock"), VLNV(name="clock_rtl"), logical_ports=[ "CLK" ], parameters=["ASSOCIATED_RESET", "ASSOCIATED_BUSIF"])

axilite_ports = [ "AWADDR", "AWPROT", "AWVALID", "AWREADY", "WDATA", "WSTRB",
                  "WVALID", "WREADY", "BRESP", "BVALID", "BREADY", "ARADDR",
                  "ARPROT", "ARVALID", "ARREADY", "RDATA", "RRESP", "RVALID", "RREADY" ]

#XILINX_AXIMM = ipxact_bus(VLNV(name="aximm"), VLNV(name="aximm"), logical_ports=aximm_ports)

XILINX_AXILITE = ipxact_bus(VLNV(name="aximm"), VLNV(name="aximm"), logical_ports=axilite_ports)



