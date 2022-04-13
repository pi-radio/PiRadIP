from .piradip_build_base import *

import os
import pathlib

build_root = pathlib.Path(__file__).parent.parent.absolute()

INFO(f"Build root: {build_root}")

piradlib_files = []

interface_map = {}

module_list = {}

def add_library_file(file):
    piradlib_files.append(file)


def add_interface(iface_name, d):
    interface_map[iface_name] = d
    
def add_module(module_name, module_file, wrapper_name=None, description=None, display_name=None):
    module_list[module_name] = {
        'name': module_name,
        'file': module_file,
        'wrapper_name': wrapper_name,
        'description': description,
        'display_name': display_name,
        'version': "1.0"
    }
