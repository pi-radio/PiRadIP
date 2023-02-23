from pathlib import Path
import time
import sys
import os
import pexpect
import struct
from multiprocessing import Process


class Builder:
    def __init__(self, ctx, target_cls):
        self.artifacts = []
        self.steps = []
        self.ctx = ctx
        self.target = self.add_artifact(target_cls)
        
    def add_artifact(self, a_cls):
        artifact = a_cls(self)
        
        self.artifacts.append(artifact)

        if artifact.generator is not None:
            # This means we have a build step
            step = artifact.generator(self)

            self.steps.append(step)

            for a in step.inputs:
                self.add_artifact(a)
        else:
            print("Root dependency: {artifact.name}")

        
        return artifact
            
        
        
