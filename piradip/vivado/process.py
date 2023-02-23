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
from prompt_toolkit import print_formatted_text

from .messages import VivadoMessage
from .msghandler import LoggingHandler

class VivadoTCLCommand:
    def __init__(self, wrapper, line, timeout, echo, accept):
        self.msgs = []
        self.wrapper = wrapper
        self.line = line
        self.timeout = timeout
        self.echo = echo
        self.accept = accept
        self.die = False
        self.printed = False
        
    def execute(self):
        self.cmd_msgs = []

        if self.echo:
            print(line)

        self.p.send(self.line)

    @property
    def p(self):
        return self.wrapper.p
        
    def process_result(self):
        r = self.p.readline()
            
        retval = ""

        while True:
            v = self.p.expect(["Vivado%", "INFO:[^\r\n]*\r\n", "WARNING:[^\r\n]*\r\n", "ERROR:[^\r\n]*\r\n"], timeout=self.timeout)

            if self.echo:
                print(self.p.before + self.p.after)

            retval += self.p.before
                
            if v == 0:
                break
            else:
                msg = VivadoMessage(self.p.after.strip())
                
                self.wrapper.handle_message(msg)

                if msg.preserve:
                    self.msgs.append(msg)
                
                if v >= 3:
                    self.die = True
                
        return retval

class keydefaultdict(defaultdict):
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError( key )
        else:
            ret = self[key] = self.default_factory(key)
            return ret
                
class TCLVivadoWrapper:    
    def __init__(self, log_vivado=False):
        print("Launching background Vivado process")
        kwargs = {}
        self.handlers = keydefaultdict(lambda x: [ LoggingHandler(self, x) ])
        
        if log_vivado:
           kwargs["logfile"] = sys.stdout
            
        self.p = pexpect.spawnu("vivado -nolog -nojournal -notrace -mode tcl", **kwargs)
        self.p.expect("Vivado%", timeout=60)

        self.msg_tally = defaultdict(lambda: 0)

    def handle_message(self, msg):
        self.msg_tally[msg.facnum] += 1

        for h in self.handlers[msg.facility]:
            h.handle_msg(msg)
            
        if msg.display:
            if not self.cur_cmd.printed:
                self.cur_cmd.printed = True
                print(f"During execution of command \"{self.cur_cmd.line.strip()}\":")

            msg.output()

        if msg.log:
            for f in msg.log_destinations:
                print(msg, file=f)


                
    def write(self, line, timeout=30, echo=False, accept=[]):
        if line[0] == '#':
            return # Ignore comments

        self.cur_cmd = VivadoTCLCommand(self, line, timeout, echo, accept)

        self.cur_cmd.execute()

        retval = self.cur_cmd.process_result()

        if self.cur_cmd.die:
            print(f"Error Command: {line}")
            raise Exception("Vivado error")
                
        return retval.strip()

    def cmd(self, line, **kwargs):
        return self.write(f"{line}\n", **kwargs)

    def set_property(self, prop, val, obj):
        self.cmd(f"set_property -name \"{prop}\" -value \"{val}\" -objects {obj}")
