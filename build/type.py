from .piradip_build_base import *
from .sv import dump_node

class svtype:
    def parse(node):
        basetype = None
        packed_range = None
        
        try:
            basetype = r.get(node, "kDataTypePrimitive").text
        except anytree.resolver.ResolverError:
            try:
                basetype = r.get(node, "kUnqualifiedId/SymbolIdentifier").text
            except:
                basetype = "logic"
            
        try:
            packed_dimensions = r.get(node, "kPackedDimensions/kDeclarationDimensions/kDimensionRange")

            if (packed_dimensions.children[0].tag != "[" or
                packed_dimensions.children[2].tag != ':' or
                packed_dimensions.children[4].tag != ']'):
                ERROR(f"Not sure how to handle dimensions {packed_dimensions.text}")

            packed_range = (packed_dimensions.children[1].text, packed_dimensions.children[3].text)
        except anytree.resolver.ResolverError:
            pass

        return svtype(basetype, packed_range)
        
    def __init__(self, basetype=None, packed_range=None, default_range=None):
        assert (basetype == None or type(basetype) is type("")), f"{type(basetype)}"
        self.basetype = basetype if basetype != None else "logic"
        self.packed_range = packed_range
        self.default_range = default_range
        
    @property
    def typename(self):
        tn = self.basetype
        if self.packed_range is not None:
            tn += f" [{self.packed_range[0]}:{self.packed_range[1]}]"
        return tn

    @property
    def definite_range(self):
        return self.packed_range == None or (self.packed_range[0].isdigit() and self.packed_range[1].isdigit())

    def __str__(self):
        return self.typename
