from .structure import add_library_file, add_interface, add_module
from .interfaces import build_interfaces
from .modules import build_modules, wrap_modules

def build_all():
    print("Building all...")
    build_interfaces()

    build_modules()

    wrap_modules()

