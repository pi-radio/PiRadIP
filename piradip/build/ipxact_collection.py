from .ipxact_base import *
from .ipxact_node import *

class IPXACTCollectionBase(IPXACTNode):
    def __init__(self, parent, name, classtype):
        super(IPXACTCollectionBase, self).__init__(parent, S(name))
        self.classtype = classtype

    def append(self, n):
        assert isinstance(n, self.classtype), f"Incorrect type {type(n)} -- expected {self.classtype}"
        self.node.append(n.node)

    def add(self, *args, **kwargs):
        n = self.classtype(self, *args, **kwargs)
        self.append(n)
        return n

    def add_subclass(self, subclass, *args, **kwargs):
        n = subclass(self, *args, **kwargs)
        self.append(n)
        return n

    
    def resolve(self):
        if len(self.children) == 0:
            return
        super(IPXACTCollectionBase, self).resolve()
        

class IPXACTCollection(IPXACTCollectionBase):
    def __init__(self, parent, name, classtype):
        super(IPXACTCollection, self).__init__(parent, name, classtype)
        

class IPXACTNamedCollection(IPXACTNode):
    def __init__(self, parent, name, itemname, classtype):
        super(IPXACTNamedCollection, self).__init__(parent, S(name, S.name(itemname)))
        self.classtype = classtype
        
    def add(self, *args, **kwargs):
        n = self.classtype(self, *args, **kwargs)
        self.append(n)
        return n

    
class IPXACTGroupCollection(IPXACTCollectionBase):
    def __init__(self, parent, name, classtype):
        super(IPXACTGroupCollection, self).__init__(parent, name, classtype)
        self.groups = [ [], [] ] # Cheating here

    def add(self, group, *args, **kwargs):
        n = self.classtype(self, *args, **kwargs)
        self.groups[group].append(n)
        return n

    def resolve(self):
        for l in self.groups:
            for i in l:
                self.children.append(i)

        super(IPXACTGroupCollection, self).resolve()

