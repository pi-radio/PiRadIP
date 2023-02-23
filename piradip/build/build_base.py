from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

from .artifact import Artifact, File, VivadoCheckpoint
from .step import BuildStep    
from .builder import Builder        

class VivadoStep(BuildStep):
    # This one will do the load.
    pass

class ShellStep(BuildStep):
    # This will do the command
    pass


class BD(File):
    @property
    def path(self):
        return Path(self.ctx.bd_path)

class InMemoryBD(VivadoCheckpoint):
    path = Path("dookie.bd")
    pass
    
class LoadBD(VivadoStep):
    inputs = [ BD ]
    outputs = [ InMemoryBD ]
    
    def run(self):
        # if we ran create we don't need this
        self.cmd(f"read_bd {self.path}")
    


