from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import FormattedText
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

class VivadoMessage:
    msg_re = re.compile(f"(?P<level>ERROR|WARNING|INFO): \[(?P<facility>[^\s]+) (?P<maj>[\d]+)-(?P<min>[\d]+)\] (?P<msg>.*)")
    file_line_re = re.compile(r"(?P<msg>.*) \[(?P<file>[^:]+):(?P<line>[0-9]+)\]")
    module_re = re.compile("module '?(?P<module>[A-Za-z_][A-Za-z_0-9]*)'?")

    def __init__(self, s):
        self.display = True
        self.log = True
        self.log_destinations = []
        self.preserve = True
        self.style = ''
        
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

    @property
    def formatted(self):
        return FormattedText([(self.style, str(self))])
    
    def output(self):
        print_formatted_text(self.formatted)
