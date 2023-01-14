from functools import cached_property, wraps
import re

suffix_re = re.compile(r'[0-9]+$')

def suffixize(s):
    m = suffix_re.match(s)

    if m is None:
        return s + "_1"

    s[slice(*m.span)] = str(int(m.group()) + 1)

    return s

def bdactive(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.make_active()
        return f(self, *args, **kwargs)
    return wrapper

def get_property_list(l):
    if len(l) > 1:
        return "-dict [list " + " \\\n".join([f"{k} {{{v}}}" for k, v in l]) + f"]"

    return f"{l[0][0]} {{{l[0][1]}}}" 
        
def get_property_dict(d):
    if isinstance(d, list):
        return get_property_list(d)
    return get_property_list([(k, v) for k, v in d.items()])

class BDObj:
    root = False
    hier = False
    intf = False
    net = False
    pin = False
    port = False
    ip = False
    
    def __init__(self, parent, name):
        assert(name is not None)
        if parent is not None:
            self.parent = parent
        self.name = name

    @cached_property
    def vivado(self):
        return self.parent.vivado

    def cmd(self, s, **kwargs):
        return self.vivado.cmd(s, **kwargs)
    
    @cached_property
    def bd(self):
        if self.parent == None:
            return self
        return self.parent.bd
            
    @cached_property
    def path(self):
        if self.parent is not None:
            pp = self.parent.path
            if pp[-1] == "/":
                return pp + self.name
            return pp + "/" + self.name
        return "/"

    @cached_property
    def upath(self):
        if self.parent is not None:
            pp = self.parent.path
            if pp[-1] == "_":
                return pp + self.name
            return pp + "_" + self.name
        return "_"

    @property
    def obj(self):
        raise Exception("Not a valid BD class")

    def set_property(self, prop, val):
        self.vivado.set_property(prop, val, self.obj)

    def set_property_list(self, d):
        self.cmd(f"set_property {get_property_dict(d)} {self.obj}")
            
    def get_property(self, prop):
        return self.cmd(f"get_property {prop} {self.obj}")

    def list_properties(self):
        return self.cmd(f"list_property {self.obj}").split()

    def get_properties_dict(self):
        return { k:self.get_property(k) for k in self.list_properties() }
    
    def dump_properties(self):
        lp = self.list_properties()

        for name in lp:
            print(f"{self.name}: {name}: {self.get_property(name)}")

    def get_active(self):
        return self.bd.get_current()
        
    def make_active(self):
        self.bd.set_current(self)

    def clear_active(self):
        self.bd.set_current(None)
