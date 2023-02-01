from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process


class Builder:
    def __init__(self, ctx):
        self.artifacts = []
        self.steps = []
        self.ctx = ctx

    def add_artifact(self, a_cls):
        
