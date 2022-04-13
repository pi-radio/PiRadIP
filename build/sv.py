from .verible_verilog_syntax import VeribleVerilogSyntax
import anytree

v = VeribleVerilogSyntax()

r = anytree.Resolver("tag")

def parse(filename):
    return v.parse_file(filename, options= { 'gen_tree': True }).tree

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
