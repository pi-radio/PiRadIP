from piradip.vivado.obj import VivadoObj

from functools import cached_property, wraps
import re
import inspect

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

class BDObj(VivadoObj):
    root = False
    hier = False
    intf = False
    net = False
    pin = False
    port = False
    ip = False
    virtual = False

    memory_aperture_size = 64*1024
    
    @cached_property
    def bd(self):
        if self.root:
            return self
        return self.parent.bd

    def add_post_synthesis_command(self, cmd):
        self.bd.project.add_post_synthesis_command(cmd)
    
    @cached_property
    def path(self):
        pp = self.parent.path
        if pp[-1] == "/":
            return pp + self.name
        return pp + "/" + self.name

    @cached_property
    def upath(self):
        pp = self.parent.path
        if pp[-1] == "_":
            return pp + self.name
        return pp + "_" + self.name        

    @property
    def children(self):
        if hasattr(self, "cells"):
            yield from self.cells

        if hasattr(self, "pins"):
            yield from self.pins

        if hasattr(self, "ports"):
            yield from self.ports
    
    @property
    def obj(self):
        raise Exception("Not a valid BD class")

    def get_active(self):
        return self.bd.get_current()
        
    def make_active(self):
        self.bd.set_current(self)

    def clear_active(self):
        self.bd.set_current(None)

    @property
    def dependencies(self):
        retval = set([ inspect.getfile(self.__class__) ])

        for c in self.children:
            retval |= c.dependencies
