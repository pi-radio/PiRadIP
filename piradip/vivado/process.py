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

DEBUG=False

global_ignore = [
    ('BD', 5, 236), # Windows path BS

    ('Synth', 8, 5544), # ROM not mapped to BRAM
    ('Synth', 8, 3332), # Sequential element unsued -- maybe not WARNINGs?
    ('Synth', 8, 6904), # LUTRAM implementation
    ('Synth', 8, 7067), # Removed DRAM
]

class TCLVivadoWrapper:
    msg_re = re.compile(f"(?P<level>ERROR|WARNING|INFO): \[(?P<facility>[^\s]+) (?P<maj>[\d]+)-(?P<min>[\d]+)\] (?P<msg>.*)")
    
    def __init__(self, log_vivado=False):
        print("Launching background Vivado process")
        kwargs = {}

        if log_vivado:
           kwargs["logfile"] = sys.stdout
            
        self.p = pexpect.spawnu("vivado -nolog -nojournal -notrace -mode tcl", **kwargs)
        self.p.expect("Vivado%", timeout=60)

        self.msg_history = []
        
    def write(self, line, timeout=30, echo=False, accept=[]):
        if line[0] == '#':
            return
        #print(line, end="")
        self.cmd_msgs = []
        self.p.send(line)

        if echo:
            print(line)
        
        r = self.p.readline()

        if DEBUG:
            print(f"COMMAND: {line}")
            print(f"ECHO: {r}")
            
        retval = ""

        die = False

        cmd_printed = False
        
        while True:
            v = self.p.expect(["Vivado%", "INFO:.*\n", "WARNING:.*\n", "ERROR:.*\n"], timeout=timeout)

            if echo:
                print(self.p.before + self.p.after)
            
            if DEBUG:
                print(f"RESULT: {v} {self.p.after}")
            
            if v == 0:
                retval += self.p.before
                break
            else:
                s = self.p.after.strip()
                
                m = self.msg_re.match(s)

                if m is not None:
                    self.cmd_msgs.append((m['level'], m['facility'], m['maj'], m['min'], m['msg']))

                    t = (m['facility'], int(m['maj']), int(m['min']))
                    
                    if v < 3 and ((t in accept) or (t in global_ignore)):
                        continue
                else:
                    assert v == 1
                    self.cmd_msgs.append(('INFO', s))


                if not cmd_printed and v > 1:
                    cmd_printed = True
                    print(f"During execution of command \"{line.strip()}\":")
                    
                print(s)
                    
                if v >= 3:
                    die = True

        self.msg_history.append((line, self.cmd_msgs))
                
        if die:
            print(f"Error Command: {line}")
            raise Exception("Vivado error")
                
        if DEBUG:
            print(f"RETVAL: {retval}")
        return retval.strip()

    def cmd(self, line, **kwargs):
        return self.write(f"{line}\n", **kwargs)

    def set_property(self, prop, val, obj):
        self.cmd(f"set_property -name \"{prop}\" -value \"{val}\" -objects {obj}")
