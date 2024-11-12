import os.path
import ptyprocess

from pathlib import Path
import functools
import sys
import re
import time
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
            print(f"   CMD: {self.line.strip()}")

        self.proc.write(self.line.encode())


    @property
    def proc(self):
        return self.wrapper.proc
        
    def process_result(self):
        def is_message(l):
            return (l.startswith("INFO:") or l.startswith("WARNING:") or
                    l.startswith("CRITICAL WARNING:") or l.startswith("ERROR:"))

        retval = ""

        msg = None

        lines = []

        msg = None
        last_line = None
        
        
        for i, l in enumerate(self.wrapper.cmd_output):
            if l.strip() == self.line.strip():
                continue

            if l.startswith("Vivado-"):
                continue

            print(f"LINE: {l}")
            
            if last_line is not None:
                if is_message(last_line):
                    if last_line.startswith("ERROR:"):
                        print(f"ERROR: {last_line}")
                        self.die = True
                        
                    if msg is not None:
                        self.wrapper.handle_message(msg)
                        
                    msg = VivadoMessage([ last_line ])
                elif msg is not None:
                    msg.msg += "\n" + last_line                    

            # skip the command echo
            if i != 0:
                last_line = l                
                lines += [ l ]

        if msg is not None:
            self.wrapper.handle_message(msg)
                
        return last_line
                

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

        kwargs['maxread'] = 32 * 1024

        self.proc = ptyprocess.PtyProcess.spawn([ 'vivado', '-nolog', '-nojournal', '-notrace', '-mode', 'tcl' ],
                                                echo=False, dimensions=(80, 200))        
        
        for l in self.cmd_output:
            pass
        
        self.msg_tally = defaultdict(lambda: 0)
        self.print_all = False

    @property
    def cmd_output(self):
        buf = ""
        
        while True:
            buf += self.proc.read(1).decode()

            if buf[-1] == "\n":
                print(f"BUF: {buf[:-1]}")
                yield buf[:-1]
                buf = ""
            elif buf == "Vivado%":
                return
                
        
    def handle_message(self, msg):
        self.msg_tally[msg.facnum] += 1

        for h in self.handlers[msg.facility]:
            h.handle_msg(msg)

        if msg.level == 'ERROR':
            self.print_all = True
            
            
        if msg.display:
            if not self.cur_cmd.printed:
                self.cur_cmd.printed = True
                print(f"During execution of command \"{self.cur_cmd.line.strip()}\":")

        if msg.display or self.print_all:
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
                
        return retval.strip() if retval is not None else ""
    
    def cmd(self, line, **kwargs):
        return self.write(f"{line}\n", **kwargs)

    def set_property(self, prop, val, obj):
        self.cmd(f"set_property -name \"{prop}\" -value \"{val}\" -objects {obj}")
