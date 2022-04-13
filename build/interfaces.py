from .piradip_build_base import *
from .structure import interface_map
from .sv import dump_node, parse, get_interfaces
from .type import svtype
from .parameter import Parameter
from .port import Port, ModportPort

#
# TODO: Parse the package
#
global_type_punts = {
    'axi_resp_t': 'logic [1:0]',
    'axi_burst_t': 'logic [1:0]',
    'axi_size_t': 'logic [2:0]',
    'axi_len_t': "logic [7:0]",
    'axi_prot_t': 'logic [2:0]',
    'axi_cache_t': 'logic [3:0]',
    'axi_qos_t': 'logic [3:0]',
    'axi_region_t': 'logic [3:0]',
    'axi_lock_t': 'logic'
}

def resolve_type(name):
    return global_type_punts.get(name, name)

class Interface:
    class Modport:
        def parse(iface, n):
            modport = Interface.Modport(iface, r.get(n, 'kModportItemList/kModportItem/SymbolIdentifier').text)
    
            for d in r.get(n, 'kModportItemList/kModportItem/kParenGroup/kModportPortList').children:
                if (d.tag == 'kModportSimplePortsDeclaration'):
                    direction = d.children[0].text
                    for p in d.children[1:]:
                        if p.tag == ',':
                            continue
                        if p.tag != 'kModportSimplePort':
                            WARNING(f"WARNING: Not handling {p.tag}");
                            dump_node(p)
                            continue
                        port_name = r.get(p, 'SymbolIdentifier').text
                        ModportPort(port_name, modport, direction)
                elif (d.tag == ','):
                    pass
                else:
                    dump_node(d)
                
            return modport
        
        def __init__(self, iface, name):
            self.iface = iface
            self.name = name
            self.iface.modports[self.name] = self
            self.directions = {}
            self.ports = {}

        def __str__(self):
            return f"modport {self.name} output: {self.outputs} input: {self.inputs}"

        def __repr__(self):
            return f"modport {self.name} output: {self.outputs} input: {self.inputs}"

        @property
        def types(self):
            return self.iface.datas
        
        def resolve_type(self, typename):
            return self.iface.resolve_type(typename)
        

        

    def parse(n, idesc):
        name = r.get(n, "kModuleHeader/SymbolIdentifier").text

        iface = Interface(name, idesc)

        Parameter.parse_set(n, iface)
        Port.parse_set(n, iface)
            
        module_body = r.get(n,"kModuleItemList")


        for n in module_body.children:
            if n.tag == 'kPackageImportDeclaration':
                pass
            elif n.tag == 'kPackageImportItemList':
                pass
            elif n.tag == 'kContinuousAssignmentStatement':
                pass
            elif n.tag == 'kParamDeclaration':
                if n.children[0].tag != 'localparam':
                    WARNING("Non-local parameter")
            elif n.tag == 'kTypeDeclaration':
                iface.types[r.get(n, 'SymbolIdentifier').text] = svtype.parse(r.get(n, 'kDataType'))
            elif n.tag == 'kDataDeclaration':
                data_type = svtype.parse(r.get(n, 'kInstantiationBase/kInstantiationType/kDataType'))
                data_names = r.glob(n, 'kInstantiationBase/kGateInstanceRegisterVariableList/*/SymbolIdentifier')
                for name in data_names:
                    iface.types[name.text] = data_type
            elif n.tag == 'kModportDeclaration':
                Interface.Modport.parse(iface, n)
            else:
                dump_node(n)
                ERROR(f"Unhandled tag {n.tag}")
                
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        interfaces[name] = self
        self.params = {}
        self.ports = {}
        self.types = {}
        self.modports = {}

    @property
    def ipxdesc(self):
        return self.desc.get('ipxdesc', None) 
        
    @property
    def pdescs(self):
        return self.desc.get('parameters', {})
        
    def resolve_type(self, name):
        return resolve_type(self.types.get(name, name))


    
r = anytree.Resolver("tag")


def build_interfaces():
    interface_files = set([v['file'] for v in interface_map.values()])
    interface_names = interface_map.keys()
    
    for v in interface_files:
        INFO(f"Reading file {v}...")
        root = parse(v)

        ifaces = get_interfaces(root)

        for n in ifaces:
            name = r.get(n, "kModuleHeader/SymbolIdentifier").text

            INFO(f"Found interface {name}...")
            if name in interface_names:
                INFO(f"Parsing {name}...")
                Interface.parse(n, interface_map[name])

    existing_interfaces = set(interfaces.keys())
                
    if existing_interfaces != interface_names:
        ERROR(f"Could not find all interfaces: Missing: {existing_interfaces.difference(interface_names)}")
            
            
