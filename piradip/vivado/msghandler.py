from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys
import re
from functools import cached_property
from collections import defaultdict

class VivadoMessageHandler:    
    def __init__(self, wrapper, facilities):
        self.wrapper = wrapper

        if isinstance(facilities, str):
            self.facilities = [ facilities ]
        else:
            self.facilities = facilities
            
        for facility in self.facilities:
            self.wrapper.handlers[facility].append(self)

class LoggingHandler:
    suppress = {
        ('BD', 5, 236),
        ('Synth', 8, 5544), # ROM not mapped to BRAM
        ('Synth', 8, 3332), # Sequential element unsued -- maybe not WARNINGs?
        ('Synth', 8, 6904), # LUTRAM implementation
        ('Synth', 8, 7067), # Removed DRAM
    }
    
    def __init__(self, wrapper, facility):
        self.wrapper = wrapper
        self.facility = facility
        self.suppress = { x[1:] for x in self.suppress if x[0] == facility }

        if facility is None:
            facility = "general"
        
        self.log_dir = Path("logs") / facility
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.logs = { "ERROR": open(self.log_dir / "error.log", "w"),
                      "WARNING": open(self.log_dir / "warning.log", "w"),
                      "INFO": open(self.log_dir / "info.log", "w") }

        self.default_log = open(self.log_dir / "other.log", "w");
                
    def handle_msg(self, msg):
        msg.log_destinations.append(self.logs.get(msg.level, self.default_log))
