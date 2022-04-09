import sys
import anytree
import re

r = anytree.Resolver("tag")

PiRadIP_Version = "1.0"


DEBUG=1

def debug_print(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

def error(*args, **kwargs):
    print(*args, **kwargs)
    sys.exit(-1)

interfaces = {}
modules = {}
