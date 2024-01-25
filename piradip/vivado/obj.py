from functools import cached_property
import inspect
from pathlib import Path

def encode_property(v):
    return f"{{{v}}}"

def get_property_list(l):
    if len(l) > 1:
        return "-dict [list " + " \\\n".join([f"{k} {encode_property(v)}" for k, v in l]) + f"]"

    return f"{l[0][0]} {{{l[0][1]}}}" 
        
def get_property_dict(d):
    if isinstance(d, list):
        return get_property_list(d)
    return get_property_list([(k, v) for k, v in d.items()])


class VivadoObj:
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    @property
    def children(self):
        yield from ()


    @property
    def code_deps(self):
        deps = set([self.classdef_file])

        for c in self.children:
            deps |= c.code_deps

        return deps

    @property
    def classdef_file(self):
        return inspect.getfile(self.__class__)
                    
    @cached_property
    def mtime(self):
         mtime =  Path().stat().st_mtime

         for c in children:
             mtime = max(mtime, c.mtime)
         
         return mtime
         
    @cached_property
    def vivado(self):
        return self.parent.vivado
        
    def cmd(self, s, **kwargs):
        return self.vivado.cmd(s, **kwargs)

    def set_property(self, prop, val):
        self.vivado.set_property(prop, val, self.obj)

    def set_property_list(self, d):
        print(f"set_property {get_property_dict(d)} {self.obj}")
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
