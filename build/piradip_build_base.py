import sys
import anytree
import re

r = anytree.Resolver("tag")

PiRadIP_Version = "1.0"


DEBUG_IPXACT='IPXACT:'

debug_flags = { DEBUG_IPXACT: 0 }

dump_definitions=False

def debug_print(flag, *args, **kwargs):
    if debug_flags.get(flag, 0):
        print(flag, *args, **kwargs)

        
def INFO(*args, **kwargs):
    print("INFO:", *args, **kwargs)
        
def WARN(*args, **kwargs):
    print("WARNING:", *args, **kwargs)
        
def ERROR(*args, **kwargs):
    print("ERROR:", *args, **kwargs)
    sys.exit(-1)

registered_interfaces = {}
registered_modules = {}
