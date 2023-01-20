from .piradip_build_base import *

from .ipxact_base import *

import lxml.etree
import io
import datetime
import os
import os.path

class IPXACTNode():
    def __init__(self, parent, node):
        self.node = node
        self._children = []
        self.parent = parent
        if self.parent:
            self.parent.add_child(self)

    @property
    def children(self):
        return self._children

    def add_child(self, c):
        self.children.append(c)
    
    @property
    def name(self):
        return self.node.findtext(f"{{{NS_SPIRIT}}}name")

    @name.setter
    def name(self, value):
        self.node.append(S.name(value))
    
    def append(self, n):
        self.node.append(n.node)

    def resolve(self):
        for c in self.children:
            c.resolve()

        if self.parent:
            self.parent.append(self)
