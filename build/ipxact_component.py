from .ipxact_base import *
from .ipxact_node import *
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

class IPXACTEnumeration(IPXACTNode):
    def __init__(self, parent, value):
        super(IPXACTEnumeration, self).__init__(parent, S.enumeration(value))
    
class IPXACTChoice(IPXACTNamedCollection):
    def __init__(self, parent, itemname):
        super(IPXACTChoice, self).__init__(self, parent, "choice", itemname, IPXACTEnumeration)
        
    
interrupt_sensitivity_list = IPXACTChoiceList("choice_list_99a1d2b8", [ 'LEVEL_HIGH', 'LEVEL_LOW', 'EDGE_RISING', 'EDGE_FALLING' ] )
polarity_list = IPXACTChoiceList("choice_list_9d8b0d81", [ 'ACTIVE_HIGH', 'ACTIVE_LOW' ] )

id_re = re.compile(r"([A-Za-z_][A-Za-z0-9_]+)")

def ipxact_resolve_parameters(s):
    return id_re.sub(r"spirit:decode(id(MODELPARAM_VALUE.\1))",s)

class IPXACTPort(IPXACTNode):
    direction_map = { 'input': 'in', 'output': 'out' }
        
    
    def __init__(self, parent, portname, direction, svtype=None, views=[]):
        wireType = S.wireTypeDef(S.typeName("wire"))

        for v in views:
            wireType.append(S.viewNameRef(v))

        wire = S.wire(S.direction(self.direction_map[direction]))
            
        if svtype.packed_range:
            left = S.left()
            left.attrib[f"{{{NS_SPIRIT}}}format"]="long"
            
            if svtype.packed_range[0].isdigit():
                left.text = svtype.packed_range[0]
            else:
                left.attrib[f"{{{NS_SPIRIT}}}dependency"]="("+ipxact_resolve_parameters(svtype.packed_range[0])+")"
                left.attrib[f"{{{NS_SPIRIT}}}resolve"]="dependent"
                left.text = svtype.default_range[0]
                
            right = S.right()
            right.attrib[f"{{{NS_SPIRIT}}}format"]="long"
            
            if svtype.packed_range[1].isdigit():
                right.text = svtype.packed_range[1]
            else:
                right.attrib[f"{{{NS_SPIRIT}}}dependency"]="("+ipxact_resolve_parameters(svtype.packed_range[1])+")"
                right.attrib[f"{{{NS_SPIRIT}}}resolve"]="dependent"
                right.text = svtype.default_range[1]
                
            wire.append(S.vector(left, right))

        wire.append(S.wireTypeDefs(wireType))
            
        n = S.port(S.name(portname), wire)
                
        super(IPXACTPort, self).__init__(parent, n)

class IPXACTView(IPXACTNode):
    def __init__(self, parent, name, displayName, envIdentifier=None):
        n = S.view(S.name(name), S.displayName(displayName))

        if envIdentifier is not None:
            n.append(S.envIdentifier(envIdentifier))
        
        super(IPXACTView, self).__init__(parent, n)

class IPXACTModelParameter(IPXACTNode):
    def __init__(self, parent, name, data_type, display_name, description, value):
        v = S.value(value)
        v.attrib[f"{{{NS_SPIRIT}}}format"] = "long"

        n = S.modelParameter(S.description(description), S.displayName(display_name), S.name(name), v)
        n.attrib[f"{{{NS_SPIRIT}}}dataType"] = data_type
        
        super(IPXACTModelParameter, self).__init__(parent, n)
        
class IPXACTModel(IPXACTNode):
    def __init__(self, parent):
        super(IPXACTModel, self).__init__(parent, S.model())

        self.views = IPXACTCollection(self, "views", IPXACTView)
        self.ports = IPXACTCollection(self, "ports", IPXACTPort)
        self.model_parameters = IPXACTCollection(self, "modelParameters", IPXACTModelParameter)
        
class IPXACTFileSet(IPXACTNode):
    def __init__(self, parent, name=None, files=None, node=None):
        if node is not None:
            super(IPXACTFileSet, self).__init__(parent, node)
        else:
            n = S.fileSet(
                S.name(name),
            )

            for f in files:
                fn = S.file(S.fileType(f['type']),
                                S.name(str(f['file'])))
                n.append(fn)

                for t in f.get('userFileTypes', []):
                    fn.append(S.userFileType(t))

            super(IPXACTFileSet, self).__init__(parent, n)

class IPXACTSubCoreReference(IPXACTFileSet):
    def __init__(self, parent, name):
        
        comp_mode = X.mode();
        comp_mode.attrib[f"{{{NS_XILINX}}}name"] = "copy_mode"
        comp_ref = X.componentRef(comp_mode)

        comp_ref.attrib[f"{{{NS_XILINX}}}vendor"] = "pi-rad.io"
        comp_ref.attrib[f"{{{NS_XILINX}}}library"] = "PiRadIP"
        comp_ref.attrib[f"{{{NS_XILINX}}}name"] = "PiRadIP"
        comp_ref.attrib[f"{{{NS_XILINX}}}version"] = PiRadIP_Version

        
        n = S.fileSet(
            S.name(name),
            S.vendorExtensions(
                X.subCoreRef(comp_ref)
                )
        );

        super(IPXACTSubCoreReference, self).__init__(parent, node=n)
        
        
class IPXACTComponent(IPXACTNode):
    def __init__(self, parent, vendor, library, name, version):
        n = S.component(
            S.vendor(vendor),
            S.library(library),
            S.name(name),
            S.version(version)
            )
        
        super(IPXACTComponent, self).__init__(parent, n)

        self.bus_interfaces = IPXACTGroupCollection(self, "busInterfaces", IPXACTBusInterface)
        self.memory_maps = IPXACTCollection(self, "memoryMaps", IPXACTMemoryMap)

        self.model = IPXACTModel(self)

        self.choices = IPXACTCollection(self, "choices", IPXACTChoice)
        self.file_sets = IPXACTCollection(self, "fileSets", IPXACTFileSet)

        IPXACTParameters(self)
