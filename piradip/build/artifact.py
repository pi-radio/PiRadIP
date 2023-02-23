from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

artifacts = dict()

class Artifact:
    def __init__(self, name):
        self.name = name
        assert name not in artifacts
        artifacts[name] = self
        self.generator = None
        
    def generate(self, ctx):
        self.generator(ctx)

class File(Artifact):
    def __init__(self, path):
        if not isinstance(path, Path):
            path = Path(path)
        super().__init__(str(path))
        self.path = path

    @property
    def mtime(self):
        if not self.path.exists():
            return 0

        return self.path.stat().st_mtime

