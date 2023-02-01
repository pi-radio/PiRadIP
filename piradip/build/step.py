from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

from .artifact import Artifact, File, VivadoCheckpoint


class BuildStepMetaclass(type):
    def __new__(cls, name, bases, dct):
        dct["name"] = name.lower()

        new_cls = super().__new__(cls, name, bases, dct)
        
        for a in new_cls.inputs:
            a.dependents.append(new_cls)

        for a in new_cls.outputs:
            assert a.generator is None
            a.generator = new_cls
        
        return new_cls
            
class BuildStep(metaclass=BuildStepMetaclass):
    inputs = []
    outputs = []
    
    def __init__(self, ctx):
        self.ctx = ctx        

    def check_dependencies(self, mtime):
        for i in self.inputs:
            if not i.exists:
                i.build(self.ctx)
