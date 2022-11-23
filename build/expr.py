from .piradip_build_base import *
from .svbase import *

import inspect
import bitarray
import bitarray.util

@svex("kParenGroup")
def parse_paren_group(node):
    assert_nchild(node, 3)
    assert node.children[0].tag == '('
    assert node.children[2].tag == ')'
    return svexcreate(node.children[1])

    
@svex("SymbolIdentifier")
def parse_symbol(node):
    assert_nchild(node, 0)
    return svsymbol(node.text)
    
class svunqualifiedid:
    def __init__(self, symbol, other=None):
        self.symbol = symbol
        self.other = other
        assert(self.other == None)

    def __str__(self):
        return str(self.symbol)

    def __repr__(self):
        return str(self.symbol)
    
    def __hash__(self):
        return hash(self.symbol)

    def __eq__(self, other):
        if isinstance(other, svunqualifiedid):
            return self.symbol == other.symbol
        return self.symbol == other
    
    @property
    def const(self):
        return False

    def subst(self, ns):
        return svunqualifiedid(subst(self.symbol, ns), self.other)
    
@svex("kUnqualifiedId")
def parse_id(node):
    if len(node.children) == 1:
        return svexcreate(node.children[0])
    
    assert_nchild(node, 2)
    assert svexcreate(node.children[1]) == None
    return svexcreate(node.children[0])
    
svpassnode("kLocalRoot")
svpassnode("kReference")
svignorenode("kMethodCallExtension")
svignorenode("kFunctionDeclaration")

    
@svex2("kHierarchyExtension")
class svexkheirarchyextension:
    def parse(node):
        assert_nchild(node, 2)
        assert(node.children[0].tag == '.')
        return svexcreate(node.children[1])

        
@svex2("kReferenceCallBase")
class svexreferencecallbase:
    def parse(node):
        if len(node.children) == 1:
            return svexcreate(node.children[0])
        print(node.children)
        assert_nchild(node, 2)
        return svexreferencecallbase(svexcreate(node.children[0]), svexcreate(node.children[1]))

    def __init__(self, base, ext):
        self.base = base
        self.ext = ext
        print(base, ext)

    @property
    def const(self):
        return False

    def subst(self, ns):
        pass

class svexliteral:
    def __init__(self, n, width=32):
        self.n = n if not isinstance(n, svexliteral) else n.n
        self.width = width if not isinstance(n, svexliteral) else width.n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return str(self.n)

    @property
    def bits(self):
        return bitarray.util.int2ba(self.n, self.width)
        
    @property
    def const(self):
        return True
    
    @property
    def resolved(self):
        return True
    
    @property
    def unresolved(self):
        return set()
    
    @property
    def cval(self):
        return self.n

    def subst(self, ns):
        return svexliteral(self.n)

svignorenode("TK_BinBase", okay=True)
    

@svex("TK_BinDigits")
def txbindigits(node):
    return svexliteral(int(node.text, 2))

@svex("TK_DecNumber")
def tkdecnumber(node):
    return svexliteral(int(node.text))

@svex("kBaseDigits")
def parse_base_digits(node):
    assert_nchild(node, 2)
    assert_nonechild(node, 0)
    
    return svexcreate(node.children[1])

@svex("kNumber")
def parse_number(node):
    if len(node.children) == 1:
        return svexcreate(node.children[0])

    assert_nchild(node, 2)
    width = svexcreate(node.children[0])
    basedigits = svexcreate(node.children[1])
    
    return svexliteral(basedigits, width)
                       

@svex2("kBinaryExpression")
class svbinaryexpression(svexbase):
    def parse(node):
        assert_nchild(node, 3)
        return svbinaryexpression.create(svexcreate(node.children[0]), node.children[1].tag, svexcreate(node.children[2]))

    def create(t1, op, t2):
        if t1 == None:
            t1 = svexliteral(0)
        if t1.const and t2.const:
            if op == '+':
                return svexliteral(t1.cval + t2.cval)
            elif op == '-':
                return svexliteral(t1.cval - t2.cval)
            elif op == '*':
                return svexliteral(t1.cval * t2.cval)
            elif op == '/':
                return svexliteral(t1.cval // t2.cval)
        else:
            return svbinaryexpression(t1, op, t2)
            
    def __init__(self, t1, op, t2):
        self.t1 = t1
        self.op = op
        self.t2 = t2

    def __str__(self):
        return f"{self.t1}{self.op}{self.t2}"

    def __repr__(self):
        return f"({self.t1}){self.op}({self.t2})"

    @property
    def resolved(self):
        return self.t1.resolved and self.t2.resolved
    
    @property
    def unresolved(self):
        return self.t1.unresolved | self.t2.unresolved
    
    @property
    def const(self):
        return self.t1.const and self.t2.const

    def subst(self, ns):
        return svbinaryexpression.create(self.t1.subst(ns), self.op, self.t2.subst(ns))

        
svlistnode("kExpressionList", [ "kExpression" ])

@svex2("kConcatenationExpression")
class svconcatexpression:
    def parse(node):
        assert_nchild(node, 3)
        assert node.children[0].tag == '{'
        assert node.children[2].tag == '}'

        return svconcatexpression(svexcreate(node.children[1]))

    def __init__(self, expr_list):
        self.expr_list = expr_list

    def __repr__(self):
        return f"concat({self.expr_list})"

    @property
    def const(self):
        return self.expr_list.const

    @property
    def resolved(self):
        return self.expr_list.resolved
    
    @property
    def unresolved(self):
        return self.expr_list.unresolved
    
    def subst(self, ns):
        s = subst(self.expr_list, ns)

        if s.const:
            b = bitarray.bitarray()

            for e in self.expr_list:
                b += e.bits
                
            return svexliteral(bitarray.util.ba2int(b))
            
        return svconcatexpression(s)

        
class svrepeatexpression:
    def __init__(self, count, expr):
        self.count = count
        self.expr = expr

    def subst(self, ns):
        count = subst(self.count, ns)
        expr = subst(self.expr, ns)

        if count.const and expr.const:
            return svexliteral(bitarray.util.ba2int(count.n * expr.bits))
        
        return svrepeatexpression(subst(self.count, ns), subst(self.expr, ns))

    def __repr__(self):
        return f"repeat({self.count}, {self.expr})"

    @property
    def resolved(self):
        return self.count.resolved and self.expr.resolved
    
    @property
    def unresolved(self):
        return self.count.unresolved | self.expr.unresolved
    
    @property
    def const(self):
        return self.count.const and self.expr.const
    
@svex("kExpression")
def parse_expression(node):
    if len(node.children) == 1:
        return svexcreate(node.children[0])

    assert_nchild(node, 4)
    assert node.children[0].tag == '{'
    assert node.children[3].tag == '}'

    l1 = svexcreate(node.children[1])
    l2 = svexcreate(node.children[2])

    return svrepeatexpression(l1, l2)
    

class svrange:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def const(self):
        return self.left.const or self.right.const

    @property
    def unresolved(self):
        return self.left.unresolved | self.right.unresolved
        
    def subst(self, ns):
        return svrange(subst(self.left, ns), subst(self.right, ns))

@svex("kDimensionRange")
def parse_dimension_range(node):
    assert(node.children[0].tag == '[')
    assert(node.children[2].tag == ':')
    assert(node.children[4].tag == ']')
    
    return svrange(svexcreate(node.children[1]), svexcreate(node.children[3]))

svpassnodeopt("kPackedDimensions")
svpassnode("kDeclarationDimensions")
    

@svex("logic")
def parse_logic(node):
    return svlogic()
    
@svex("kDataTypePrimitive")
def parse_datatype_primitive(node):
    if len(node.children) == 2:
        assert svexcreate(node.children[1]) == None
    r = svexcreate(node.children[0])
    if r == None:
        r = svlogic()
    return r


@svex2("kInterfacePortHeader")
class svinterfaceportheader:
    def parse(node):
        assert_nchild(node, 3)
        assert node.children[1].tag == '.'
        interface = registered_interfaces[svexcreate(node.children[0])]
        modport = interface.modports[svexcreate(node.children[2])]
        
        return svinterfaceportheader(interface, modport)

    def __init__(self, interface, modport):
        self.interface = interface
        self.modport = modport

    def subst(self, ns):
        return svinterfaceportheader(self.interface, self.modport)

@svex2("kDataType")
class svtype:
    def parse(node):
        assert_nchild(node, 4)
        assert svexcreate(node.children[0]) == None
        assert svexcreate(node.children[2]) == None

        basetype = svexcreate(node.children[1])
        
        dimensions = svexcreate(node.children[3])

        if basetype == None:
            basetype = svlogic()
        
        return svtype(basetype, dimensions)

    def __init__(self, basetype, packed_range=None, unpacked_range=None):
        self.basetype = basetype
        self.packed_range = packed_range
        self.unpacked_range = unpacked_range
        assert self.unpacked_range == None

    def __str__(self):
        return f"{self.basetype}"+(f"[{self.packed_range.left}:{self.packed_range.right}]" if self.packed_range is not None else "")
        
    def subst(self, ns):
        newbase = subst(self.basetype, ns)
        new_packed_range = subst(self.packed_range, ns)
        new_unpacked_range = subst(self.unpacked_range, ns)
        
        if isinstance(newbase, svtype):
            # TODO -- Should make dimensions lists, etc but unnecessary for IP integrator right now
            assert not (self.vector and newbase.vector), "Can't handle two dimensions yet"
                
            if newbase.packed_range is not None:
                new_packed_range = newbase.packed_range
                
            if newbase.unpacked_range is not None:
                new_unpacked_range = newbase.unpacked_range
                
            newbase = newbase.basetype
        
        rval = svtype(newbase, new_packed_range, new_unpacked_range)

        return rval

    @property
    def is_interface_port(self):
        return isinstance(self.basetype, svinterfaceportheader)

    @property
    def typename(self):
        return f"{self.basetype}{self.packed_range}"

    @property
    def const(self):
        return self.basetype.const or self.packed_range.const or self.unpacked_range.const

    @property
    def unresolved(self):
        r = set()

        if self.basetype:
            r = r | self.basetype.unresolved

        if self.packed_range:
            r = r | self.packed_range.unresolved
            
        if self.unpacked_range:
            r = r | self.unpacked_range.unresolved
        
        return r
    
    @property
    def vector(self):
        try:
            return self.basetype.vector or (self.packed_range is not None)
        except Exception as e:
            print(f"Invalid type: {self} {type(self.basetype)}")
            sys.exit(0)
            
def svlogicvector(left, right):
    return svtype(svlogic(), svrange(svexliteral(left), svexliteral(right)))
            

class svtypedecl:
    def __init__(self, datatype, typename):
        self.datatype = datatype
        self.typename = typename

    def __str__(self):
        return f"typedef {self.datatype} {self.typename};"

    def __repr__(self):
        return f"typedef {self.datatype} {self.typename};"

    
    @property
    def const(self):
        return self.datatype.const
    
    @property
    def unresolved(self):
        return self.datatype.unresolved
    
    def subst(self, ns):
        return svtypedecl(self.typename, subst(self.datatype, ns))
    
@svex("kTypeDeclaration")
def parse_type_decl(node):
    assert_nchild(node, 5)
    assert node.children[0].tag == 'typedef'
    assert svexcreate(node.children[3]) == None
    assert node.children[4].tag == ';'

    return svtypedecl(svexcreate(node.children[1]), svexcreate(node.children[2]))
    
    sys.exit(0)




svpassnode("kUnpackedDimensions")


class svregistervariable:
    def __init__(self, name, unpacked):
        self.name = name
        self.unpacked = unpacked

@svex("kRegisterVariable")
def parse_register_variable(node):
    assert_nchild(node, 3)
    assert(svexcreate(node.children[2]) == None)

    return svregistervariable(svexcreate(node.children[0]), svexcreate(node.children[1]))
    

svpassnode("kGateInstanceRegisterVariableList")
        
@svex("kGateInstanceRegisterVariableList")
def parse_instance_register_variable_list(node):
    return svlist([ svexcreate(n) for n in filter(lambda n: n.tag != ',', node.children) ])

svpassnode("kInstantiationType")

class svinstantiation:
    def __init__(self, t, n):
        self.type = t
        self.names = n

    def __repr__(self):
        return f"{self.type} {self.names}";

@svex("kInstantiationBase")
def parse_instantiation_base(node):
    assert_nchild(node, 2)
    return svinstantiation(svexcreate(node.children[0]), svexcreate(node.children[1]))
    

@svex("kDataDeclaration")
def parse_data_declaration(node):
    assert_nchild(node, 3)

    assert(svexcreate(node.children[0]) == None)
    assert(node.children[2].tag == ';')

    return svexcreate(node.children[1])

