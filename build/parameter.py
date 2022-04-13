from .piradip_build_base import *

class Parameter:
    def parse_set(n, parent):
        pl = []

        try:
            param_root = r.get(n,"kModuleHeader/kFormalParameterListDeclaration/kParenGroup/kFormalParameterList")
            
            for param_node in param_root.children:
                if param_node.tag in [ ',' ]:
                    continue
                if param_node.tag != 'kParamDeclaration':
                    WARN(f"Not processing tag {param_note.tag}")
                    continue

                pl.append(Parameter.parse(param_node, parent))
            
        except anytree.resolver.ResolverError:
                WARN(f"Parameters: no parameters detected")

        return pl
        
    def parse(n, parent):        
        p = Parameter(r.get(n, "kParamType/SymbolIdentifier").text, parent)

        try:
            p.typename = r.get(n, "kParamType/kTypeInfo").text
        except anytree.resolver.ResolverError:
            WARN(f"Parameter {p.name}: no type detected")
        
        try:
            p.default = r.get(n, "kTrailingAssign/kExpression").text
        except anytree.resolver.ResolverError:
            WARN(f"Parameter {p.name}: no default detected")

        return p

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.parent.params[self.name] = self
        self.typename = ""
        self.default = ""


    @property
    def decl(self):
        v = f"parameter {self.typename} {self.name}"
        if self.default != "":
            v += f" = {self.default}"
        return v
    
    def get_propagate(self, prefix=""):
        return f".{self.name}({prefix}{self.name})"
            
