from .ipxact_base import *
from .ipxact_node import *
from .ipxact_collection import *
from .ipxact_parameter import IPXACTParameters

class IPXACTAddressBlock(IPXACTNode):
    def __init__(self, parent, name, aperture_size, address_width, usage):
        super(IPXACTAddressBlock, self).__init__(parent, S.addressBlock(S.name(f"{name}_mem" if usage == "memory" else f"{name}_reg")))

        param_prefix = f"{name}_MEM" if usage == "memory" else f"{name}_REG"
        
        base_address = S.baseAddress("0")
        
        base_address.attrib[f"{{{NS_SPIRIT}}}format"] = "long"
        base_address.attrib[f"{{{NS_SPIRIT}}}resolve"] = "user"

        self.node.append(base_address)
        
        mem_range = S.range(aperture_size)
        mem_range.attrib[f"{{{NS_SPIRIT}}}format"] = "long"

        self.node.append(mem_range)

        mem_width = S.width(address_width)
        mem_width.attrib[f"{{{NS_SPIRIT}}}format"] = "long"

        self.node.append(mem_width)
        
        self.node.append(S.usage(usage))
        

        IPXACTParameters(self)

        self.parameters.add("OFFSET_BASE_PARAM", f"C_{name}_BASEADDR",
                            f"ADDRBLOCKPARAM_VALUE.{name}.{param_prefix}.OFFSET_BASE_PARAM")
        self.parameters.add("OFFSET_HIGH_PARAM", f"C_{name}_HIGHADDR",
                            f"ADDRBLOCKPARAM_VALUE.{name}.{param_prefix}.OFFSET_HIGH_PARAM")

        
class IPXACTMemoryMap(IPXACTNode):
    def __init__(self, parent, name, aperture_size, address_width, usage):
        super(IPXACTMemoryMap, self).__init__(parent, S.memoryMap(S.name(name)))
        
        debug_print(DEBUG_IPXACT, f"Creating memory map {name}")

        IPXACTAddressBlock(self, name, aperture_size, address_width, usage)




class IPXACTBusInterface(IPXACTNode):
    def __init__(self, parent, name, busif_desc):
        super(IPXACTBusInterface, self).__init__(parent, S.busInterface(S.name(name)))

        self._name = name;
        
        parameters = IPXACTParameters(self)
        
        debug_print(DEBUG_IPXACT, f"Creating bus interface {name}")
        
        self.busif_desc = busif_desc

        self._port_maps = None
        
        n = S.busType();
        for k in busif_desc['busType']:
            n.attrib[f"{{{NS_SPIRIT}}}{k}"] = busif_desc['busType'][k]
        self.node.append(n)
        
        n = S.abstractionType();
        for k in busif_desc['abstractionType']:
            n.attrib[f"{{{NS_SPIRIT}}}{k}"] = busif_desc['abstractionType'][k]
        self.node.append(n)
        
    @property
    def name(self):
        return self._name
        
    @property
    def port_maps(self):
        if self._port_maps == None:
            self._port_maps = S.portMaps()
            self.node.append(self._port_maps)

        return self._port_maps
        
    def map_port(self, port_name, wrapped_name):
        debug_print(DEBUG_IPXACT, f"Mapping: {port_name}->{wrapped_name}")
        self.port_maps.append(S.portMap(S.logicalPort(S.name(port_name)), S.physicalPort(S.name(wrapped_name))))
                
    def make_slave(self, memory_map = None):
        if memory_map:
            debug_print(DEBUG_IPXACT, f"Adding memory map reference {memory_map.name}")
            memory_map_ref = S.memoryMapRef()
            memory_map_ref.attrib[f"{{{NS_SPIRIT}}}memoryMapRef"] = memory_map.name
            
            self.node.append(S.slave(memory_map_ref))
        else:
            self.node.append(S.slave())

    def make_master(self):
        self.node.append(S.master())
        




