import os
import pathlib

build_root = pathlib.Path(__file__).parent.parent.absolute()

print(f"Build root: {build_root}")

piradlib_files = []

interface_list = []

module_list = {}

def add_library_file(file):
    piradlib_files.append(file)


def add_interface(iface_name, iface_file):
    interface_list.append({'name': iface_name, 'file': iface_file})
    
def add_module(module_name, module_file, wrapper_name=None, description=None, display_name=None):
    module_list[module_name] = {
        'name': module_name,
        'file': module_file,
        'wrapper_name': wrapper_name,
        'description': description,
        'display_name': display_name,
        'version': "1.0"
    }
