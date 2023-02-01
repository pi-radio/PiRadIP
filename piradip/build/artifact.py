from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

from .builder import Builder

class Artifact:
    dependents = []
    generator = None

    @classmethod
    def build(cls, ctx):
        builder = Builder(ctx)

        builder.add_artifact(cls)

        
        
    def __init__(self, ctx):
        self.builder = self.generator(ctx)

    @property
    def uptodate(self):
        if not self.exists:
            return False
        

    @property
    def exists(self):
        return False
        
    @property
    def mtime(self):
        return 0
        
        
class File(Artifact):
    @property
    def exists(self):
        return self.path.exists()
    
    @property
    def mtime(self):
        print(f"Checking mtime for {self.path}")
        return self.path.stat().st_mtime


    
class VivadoCheckpoint(File):
    pass
