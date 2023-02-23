from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process

from .artifact import *

build_states = dict()

class StartState:
    def __init__(self):
        self.name = "start"
        self.inputs = []
        self.outputs = []
        self.start_state = None
        build_states[self.name] = self

    def build(self):
        return

    def load(self):
        return
    
    @property
    def mtime(self):
        return 0
        
StartState()
    
class BuildState:
    def __init__(self, name, start_state, output_files=None):
        self.name = name
        self.start_state = build_states[start_state]
        self.output_files = map(File, output_files) if output_files is not None else []

        build_states[name] = self

    def add_outputs(self, *args):
        for artifact in args:
            self.outputs.append(artifact)
            assert artifact.generator == None
            artifact.generator = self
        
    @property
    def inputs(self):
        return self.start_state.outputs

    @property
    def outputs(self):
        return self.state_files
    
    @property
    def mtime(self):
        retval = 0
        
        for i in self.output_files:
            retval = min(retval, i.mtime)

        return retval

    def generate(self):
        print(f"Generating {self.name}")
    
    def build(self):
        # First, find the earliest up-to-date build state
        states = [ self ]
        while states[0].start_state is not None:
            states = [ states[0].start_state ] + states

        while states[0].mtime < states[1].mtime and len(states) > 1:
            states = states[1:]

        print(f"Build starting at: {states[0].name}")

        states[0].load()

        states = states[1:]
                
        for s in states:
            s.generate()

