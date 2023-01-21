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

DEBUG=False

global_ignore = [
    ('BD', 5, 236), # Windows path BS

    ('Synth', 8, 5544), # ROM not mapped to BRAM
    ('Synth', 8, 3332), # Sequential element unsued -- maybe not WARNINGs?
    ('Synth', 8, 6904), # LUTRAM implementation
    ('Synth', 8, 7067), # Removed DRAM
]

class VivadoMessage:
    msg_re = re.compile(f"(?P<level>ERROR|WARNING|INFO): \[(?P<facility>[^\s]+) (?P<maj>[\d]+)-(?P<min>[\d]+)\] (?P<msg>.*)")
    file_line_re = re.compile(r"(?P<msg>.*) \[(?P<file>[^:]+):(?P<line>[0-9]+)\]")
    module_re = re.compile("module '?(?P<module>[A-Za-z_][A-Za-z_0-9]*)'?")

    def __init__(self, s):
        n = s.find(":")
        
        self.level = s[:n]
        self.facility = None
        self.major = None
        self.minor = None

        s = s[n+2:]

        if s[0] == "[":
            n = s.find("]")
            mn = s[1:n]

            try:
                self.facility, mn = mn.split()
                s = s[n+1:]
                self.major, self.minor = mn.split("-")
                try:
                    self.major = int(self.major)
                    self.minor = int(self.minor)
                except:
                    print(f"Unhandled message number: {mn} {self.facility}")
            except:
                self.facility, self.major = mn.split("-")
                self.minor = None
                
        self.msg = s.strip()
            
        if self.msg[-1] == "]":
            n = self.msg.rfind("[")
            ss = self.msg[n+1:-1]
            try:
                self.filename, self.line = ss.split(":")
                self.line = int(self.line)
            except:
                print(f"Thought file, line: {self.msg}  {ss}")
                self.filename = None
                self.line = None
            else:
                self.msg = self.msg[:n-1]
        else:
            self.filename = None
            self.line = None


    def __repr__(self):
        s = ""
        if self.facility is not None:
            s += f"{self.facility}: "
        s += f"{self.level}: "
        if self.filename is not None:
            s += f"{self.filename}:{self.line}: "
        if self.major is not None:
            if self.minor is not None:
                s += f"{self.major}-{self.minor}: "
        s += self.msg

        return s

    @property
    def number(self):
        return (self.major, self.minor)

    @property
    def facnum(self):
        return (self.facility, self.major, self.minor)

    
    @cached_property
    def module(self):
        m = self.module_re.search(self.msg)

        if m is not None:
            return m['module']

        return None
        
class VivadoMessageHandler:    
    def __init__(self, wrapper, facilities):
        self.wrapper = wrapper

        if isinstance(facilities, str):
            self.facilities = [ facilities ]
        else:
            self.facilities = facilities
            
        for facility in self.facilities:
            self.wrapper.handlers[facility].append(self)



class TCLVivadoWrapper:
    
    def __init__(self, log_vivado=False):
        print("Launching background Vivado process")
        kwargs = {}
        self.handlers = defaultdict(list)
        
        if log_vivado:
           kwargs["logfile"] = sys.stdout
            
        self.p = pexpect.spawnu("vivado -nolog -nojournal -notrace -mode tcl", **kwargs)
        self.p.expect("Vivado%", timeout=60)

        self.msg_history = []

        self.msg_tally = defaultdict(lambda: 0)

    def handle_message(self, msg):
        
        do_print = True

        self.msg_tally[msg.facnum] += 1

        self.cmd_msgs.append(msg)
        
        for h in self.handlers[msg.facility]:
            if h.handle_msg(msg):
                do_print = False
                            
            if msg.level != 'ERROR' and (msg.number in global_ignore):
                do_print = False

        if do_print:
            if not self.cmd_printed:
                self.cmd_printed = True
                print(f"During execution of command \"{self.cur_cmd.strip()}\":")

            print(msg)

                
    def write(self, line, timeout=30, echo=False, accept=[]):
        self.cur_cmd = line
        
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

        self.cmd_printed = False
        
        while True:
            v = self.p.expect(["Vivado%", "INFO:.*\r\n", "WARNING:.*\r\n", "ERROR:.*\r\n"], timeout=timeout)

            if echo:
                print(self.p.before + self.p.after)
            
            if DEBUG:
                print(f"RESULT: {v} {self.p.after}")
            
            retval += self.p.before
            
            if v == 0:
                break
            else:
                msg = VivadoMessage(self.p.after.strip())

                self.handle_message(msg)
                    
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
