from .ipxact_base import *
from .ipxact_node import *
from .ipxact_collection import *

class IPXACTParameter(IPXACTNode):
    def __init__(self, parent, name, value, paramid=None, displayName = None, description=None, value_attr=None):
        debug_print(DEBUG_IPXACT, f"Adding parameter {name} to {parent.parent.name} value {value} id {paramid}")

        n = S.parameter()

        n.append(S.name(name));

        nv = S.value(value)

        if (paramid != None):
            nv.attrib[f"{{{NS_SPIRIT}}}id"] = paramid

        n.append(nv)

        if value_attr is not None:
            for k,v in value_attr.items():
                nv.attrib[k] = v

        if displayName is not None:
            n.append(S.displayName(displayName))

        if description is not None:
            n.append(S.description(description))
                 
        super(IPXACTParameter, self).__init__(parent, n)


class IPXACTParameters(IPXACTCollection):
    def __init__(self, parent):
        super(IPXACTParameters, self).__init__(parent, "parameters", IPXACTParameter)
        parent.parameters = self

    def resolve(self):
        super(IPXACTParameters,self).resolve()

