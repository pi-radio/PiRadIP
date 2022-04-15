from .piradip_build_base import *

from .sv import *



class svparametertype:
    def __init__(self, basetype,  packed_dimensions, name, unpacked_dimensions):
        self.basetype = basetype
        if self.basetype == None:
            self.basetype = svinteger()
            
        self.name = name
        self.packed_dimensions = packed_dimensions
        self.unpacked_dimensions = unpacked_dimensions

    
class svparameter:
    def __init__(self, paramtype, default, local):
        self.basetype = paramtype.basetype
        self.name = paramtype.name
        self.packed_dimensions = paramtype.packed_dimensions
        self.basetype = paramtype.basetype        
        self.unpacked_dimensions = paramtype.unpacked_dimensions
        self.default = default
        self.local = local
        assert self.unpacked_dimensions == None

    
    def subst(self, ns):
        return svparameter(
            svparametertype(
                subst(self.basetype, ns),
                subst(self.packed_dimensions, ns),
                subst(self.name, ns),
                subst(self.unpacked_dimensions, ns)
            ),
            subst(self.default, ns),
            self.local
        )

    @property
    def decl(self):
        v = f"parameter {self.basetype}"
        if self.packed_dimensions:
            v += f" {self.packed_dimensions}"
        v += f" {self.name}"
        if self.unpacked_dimensions:
            v += f" {self.unpacked_dimensions}"
        if self.default:
            v += f" = {self.default}"
        return v

@svex("kParamType")
def parse_param_type(node):
    assert_nchild(node, 4)

    basetype = svexcreate(node.children[0])
    packed_dimensions = svexcreate(node.children[1])
    name = svexcreate(node.children[2])
    unpacked_dumensions = svexcreate(node.children[3])

    return svparametertype(*[ svexcreate(i) for i in node.children ])

svlistnode("kFormalParameterList", [ "kParamDeclaration" ])


@svex("kTrailingAssign")
def parse_trailing_assign(node):
    assert_nchild(node, 3)
    assert node.children[0].tag == '='
    assert svexcreate(node.children[2]) == None

    return svexcreate(node.children[1])
        
@svex("kParamDeclaration")
def parse_parameter(node):
    nchildren = len(node.children)
    assert nchildren in [3, 4], "Unexpected number of children {nchildren} {node.children}"
    assert(node.children[0].tag in [ 'parameter', 'localparam' ])
    if nchildren == 4:
        assert node.children[3].tag == ';'
        
    return svparameter(svexcreate(node.children[1]), svexcreate(node.children[2]), node.children[0].tag == 'localparam')


@svex("kFormalParameterListDeclaration")
def parse_formal_parameter_list_decl(node):
    assert_nchild(node, 2)
    assert node.children[0].tag == '#'
    return svexcreate(node.children[1])

@svex("kTypeInfo")
def parse_type_info(node):
    assert_nchild(node, 3)
    assert svexcreate(node.children[1]) == None
    assert svexcreate(node.children[2]) == None
    return svexcreate(node.children[0])
