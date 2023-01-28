from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

class Artifact:
    dependents = []
    generator = None

    @classmethod
    def build(self, ctx):
        print("Build")
        
class File(Artifact):
    @property
    def mtime(self):
        return self.path.stat().st_mtime
    
class VivadoCheckpoint(File):
    pass
    
class BuildStepMetaclass(type):
    def __new__(cls, name, bases, dct):
        dct["name"] = name.tolower()

        for a in inputs:
            a.dependents.append(self)

        for a in outputs:
            assert a.generator is None
            a.generator = self
        
        x = super().__new__(cls, name, bases, dct)
        
    pass
    
class BuildStep(BuildStepMetaclass):
    def __init__(self, ctx):
        self.ctx = ctx        
        

class VivadoStep(BuildStep):
    # This one will do the load.
    pass

class ShellStep(BuildStep):
    # This one will do the load.
    pass


class BD(File):
    @property
    def path(self):
        return Path(self.ctx.bd_path)

class InMemoryBD(VivadoCheckpoint):
    pass

    
class LoadBD(VivadoStep):
    inputs = [ BD ]
    outputs = [ InMemoryBD ]
    
    def run(self):
        # if we ran create we don't need this
        self.cmd(f"read_bd {self.path}")
    


class Context:
    @property
    def bd_path(self):
        return "dookie.bd"

c = Context()

InMemoryBD.build(c)
