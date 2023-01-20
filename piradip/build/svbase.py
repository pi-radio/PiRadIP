import traceback

from .verible_verilog_syntax import VeribleVerilogSyntax
from .piradip_build_base import *
import anytree
import functools
import operator
import sys

v = VeribleVerilogSyntax()

r = anytree.Resolver("tag")

def parse(filename):
    try:
        retval = v.parse_file(filename, options= { 'gen_tree': True }).tree

        if retval == None:
            ERROR(f"Failed to parse file {filename}")

        return retval
    except Exception as e:
        ERROR(f"Failed to parse file {filename}: {e}")
    
def dump_node(header, node):
    print(header)
    for p, _, t in anytree.RenderTree(node):
        print(f"DUMP: {p}{t}")

def get_interfaces(node):
    v = anytree.search.findall_by_attr(node, 'kInterfaceDeclaration', name='tag')

    return list(v) if type(v) == tuple else [ v ]

def get_modules(node):
    v = anytree.search.findall_by_attr(node, 'kModuleDeclaration', name='tag')

    return list(v) if type(v) == tuple else [ v ]

def svinspect(node):
    print(f"{node} {node.children}")

svexpression_handlers = {}

    
class svexbase:
    def __init__(self, node):
        self._node = node
        self.children = [ svexcreate(c) for c in node.children ]
    
class svlist:
    def join(n1, n2):
        if isinstance(n1, svlist):
            n1 = n1.l
        elif isinstance(n1, list):
            pass
        else:
            n1 = [ n1 ]
            
        if isinstance(n2, svlist):
            n2 = n2.l
        elif isinstance(n2, list):
            pass
        else:
            n2 = [ n2 ]

        return svlist(n1 + n2, 'join')
    
    def __init__(self, l, tag="list"):
        self.tag=tag
        self.l = list(filter(None, l))

    def __iter__(self):
        return iter(self.l)

    def _flatten(self):
        r = []

        for i in self.l:
            r += i._flatten() if isinstance(i, svlist) else [ i ] 

        return r

    def __str__(self):
        return f"<({self.tag}| " + ", ".join([str(i) for i in self.l]) + " |>"
            
    def __repr__(self):
        return f"<{self.tag}| " + ", ".join([str(i) for i in self.l]) + " |>"

    @property
    def const(self):
        return all([ i.const for i in self.l ])

    @property
    def resolved(self):
        return all([ i.resolved for i in self.l ])
    
    @property
    def unresolved(self):
        if(len(self.l) > 1):
            return functools.reduce(set.union, [ i.unresolved for i in self.l ], set())
        elif(len(self.l) == 1):
            return self.l[0].unresolved
        
        return set()
    
    def flatten(self):    
        return svlist(self._flatten(), self.tag)

    
    def prepend(self, n):
        return svlist([ n ] + self.l, self.tag)

    def subst(self, ns):
        return svlist([ subst(i, ns) for i in self.l ])

class svflatlist(svlist):
    def __init__(self, l, tag):
        super(svflatlist, self).__init__(l, tag)
        self.l = self._flatten()

    
class _svkeyword:
    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, svsymbol):
            return self.name == other.name
        return self.name == other

    @property
    def resolved(self):
        return True
    
    @property
    def unresolved(self):
        return set()
    
    def subst(self, ns):
        return self.name


        
def svkeyword(tag):
    class token(_svkeyword):
        name = tag
        def __init__(self):
            pass

        @property
        def vector(self):
            return False
        
        def subst(self, ns):
            return token()

    def tokenwrapper(node):
        return token()

    
    svexpression_handlers[tag] = tokenwrapper
    return token

svkeywords = [ "integer", "logic", "output", "input", "wire", "reg" ]

for k in svkeywords:
    globals()[f"sv{k}"] = svkeyword(k)

    


def svex(tag):
    def inner(c):
        svexpression_handlers[tag] = c

        def nodewrapper(node):
            assert(node.tag == tag)
            return c(node)
        
        return nodewrapper
    
    return inner

def svex2(tag):
    def inner(c):
        svexpression_handlers[tag] = c.parse
        return c
        
    return inner

class svunk:
    def __init__(self, node):
        print(f"Not handling node with tag {node.tag} yet children: {len(node.children)} {node.children}")
        sys.exit(0)

class svnull:
    def __init__(self, node):
        print(f"Node class: {node.__class__}")

def subst(n, ns):
    if n != None:
        if isinstance(n, str):
            return ns.get(n,n)
        return n.subst(ns)
    return None

        
def svexcreate(node):
    if hasattr(node, 'tag'):
        try:
            return svexpression_handlers.get(node.tag, svunk)(node)
        except Exception as e:
            traceback.print_exception(*sys.exc_info())
            print(f"FAILURE AT NODE {node} {e}")
            sys.exit(0)
    else:
        return None
    

def assert_nchild(node, n):
    assert len(node.children) == n, f"SVEXPR: expected {n} argument for node tag {node.tag} {len(node.children)} {node.children}"

def assert_nonechild(node, n):
    assert svexcreate(node.children[n]) == None, f"SVEXPR: expected child {n} to be none for node tag {node.tag} {len(node.children)} {node.children}"
    

    
def _svexpassopt(node):
    if len(node.children) == 0:
        return None
    assert_nchild(node, 1)
    return svexcreate(node.children[0])
    
def _svexpass(node):
    assert_nchild(node, 1)
    return svexcreate(node.children[0])

def _dumpnode(node):
    print(f"dumpnode: {node.tag} {node.children}")
    sys.exit(0)


    
def svpassnodeopt(tag):
    svexpression_handlers[tag] = _svexpassopt

def svpassnode(tag):
    svexpression_handlers[tag] = _svexpass
    
def svdumpnode(tag):
    svexpression_handlers[tag] = _dumpnode

def _svparselist(children, tag, childTypes, listclass):
    l = []
    try:
        for c in children:
            if not hasattr(c, 'tag'):
                print("NULL NODE FOUND")
                continue
            
            if c.tag in  [ ',' ]:
                continue
                
            assert c.tag in childTypes, f"Found improper tag in list {c.tag} expected {childTypes}"

            l.append(svexcreate(c))
    except Exception as e:
        print(f"Failed to parse list: children: {children} tag: {tag} childTypes: {childTypes}")
        raise e
        
    return listclass(l, tag=tag)

def svlistnode(tag, childTypes, listclass=svlist):
    def listwrapper(node):
        return _svparselist(node.children, node.tag, childTypes, listclass)

    svexpression_handlers[tag] = listwrapper

def svenclosedlistnode(tag, childTypes, enclosing, listclass=svlist):
    def listwrapper(node):
        assert node.children[0].tag == enclosing[0], f"Expecting {enclosing[0]} got {node.children[0].tag}"
        assert node.children[-1].tag == enclosing[1], f"Expecting {enclosing[1]} got {node.children[-1].tag}"
        return _svparselist(node.children[1:-1], node.tag, childTypes, listclass)

    svexpression_handlers[tag] = listwrapper
    
    
    
def svignorenode(tag, okay=False):
    def _svignorenode(node):
        if not okay: WARN(f"Ignoring {node.tag} {node.text}")
        return None
    svexpression_handlers[tag] = _svignorenode


class svsymbol(str):
    def __new__(cls, content):
        return super().__new__(cls, content)
    
    def subst(self, ns):
        if show_substitutions:
            print(f"SUBST: {self}=>{ns.get(self,self)}")
        return ns.get(self, self)

    @property
    def resolved(self):
        return False

    @property
    def vector(self):
        return False
    
    @property
    def unresolved(self):
        return set([ self ])
    
    @property
    def const(self):
        return False

svignorenode('kPackageImportDeclaration', okay=True)
svignorenode('kPackageImportItemList', okay=True)
svignorenode('kContinuousAssignmentStatement', okay=True)
svignorenode('kConditionExpression')
svignorenode('kSystemTFCall', okay=True)
svignorenode('kActualParameterList', okay=True)
svignorenode('kGateInstance', okay=True)
svignorenode('kAlwaysStatement', okay=True)
svignorenode('kGenerateRegion')
svignorenode('kGenvarDeclaration')
svignorenode('kStructType')
svignorenode('kInitialStatement')

module_item_list = [
    'kParamDeclaration',
    'kDataDeclaration',
    'kPackageImportDeclaration',
    'kTypeDeclaration',
    'kModportDeclaration',
    'kContinuousAssignmentStatement',
    'kAlwaysStatement',
    'kGenerateRegion',
    'kGenvarDeclaration',
    'kFunctionDeclaration',
    'kInitialStatement'
]

