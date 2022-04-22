from .piradip_build_base import registered_modules, registered_interfaces
from .sv import parse, svexcreate
from .structure import *
from .modules import get_modules, WrapperModule
from .interfaces import get_interfaces
from .ipxact_library import IPXACTLibrary
from .ipxact import IPXACTModule
from .ipx import IPXScript, TCLScript
from .xilinx import template_bd_tcl

def build_interfaces():
    interface_files = set([v.file for v in interface_map.values()])
    interface_names = interface_map.keys()
    
    for v in interface_files:
        INFO(f"Reading file {v}...")
        root = parse(v)

        ifaces = get_interfaces(root)

        for n in ifaces:
            name = r.get(n, "kModuleHeader/SymbolIdentifier").text

            INFO(f"Found interface {name}...")
            if name in interface_names:
                INFO(f"Parsing {name}...")
                iface = svexcreate(n)

    existing_interfaces = set(registered_interfaces.keys())
                
    if existing_interfaces != interface_names:
        ERROR(f"Could not find all interfaces: Missing: {existing_interfaces.difference(interface_names)}")


def build_modules():
    module_files = set([ v.file for _, v in module_map.items() ])
    module_names = set([ v for v in module_map ])
    
    for filename in module_files:
        root = parse(filename)

        module_nodes = get_modules(root)

        for n in module_nodes:
            name = r.get(n, "kModuleHeader/SymbolIdentifier").text

            if name in module_names:
                svexcreate(n)


wrapper_modules = {}
                
def wrap_modules():
    for m in registered_modules.values():
        w = WrapperModule(m)
        wrapper_modules[w.name] = w
        
        os.makedirs(w.desc.wrapper_verilog_path.parent, exist_ok=True)
        os.makedirs(w.desc.wrapper_xgui_path.parent, exist_ok=True)
        os.makedirs(w.desc.wrapper_bd_tcl_path.parent, exist_ok=True)
        
        INFO(f"Generating wrapper {w.name} for {m.name} at {w.desc.wrapper_verilog_path}")
        
        f = open(w.desc.wrapper_verilog_path, "w")

        w.generate_verilog(f)

        """
        INFO(f"Generating IP-XACT for {w.name} at {w.desc.wrapper_xml}...")
        os.makedirs(w.desc.wrapper_xml.parent, exist_ok=True)

        f = open(m.wrapper_xml, "w")
        """
        
        l = IPXScript(w)
        
        l.generate()

        f = open(w.desc.ipx_generate_script, "w")
        
        print(l.body, file=f)

        f = open(w.desc.wrapper_xgui_path, "w")

        print(l.xgui.body, file = f)

        f = open(w.desc.wrapper_bd_tcl_path, "w")

        print(l.bd.body, file = f)
        
def build_libraries():
    for lib in library_map.values():
        if False and lib.up_to_date:
            INFO(f"Not rebuilding {lib.xml_path} -- up to date")
            continue
        
        ipxlib = IPXACTLibrary(lib)
        
        ipxlib.export_ipxact()


def make_generate_all():
    tcl = TCLScript()

    tcl.cmd("set prev_path [pwd]")
    tcl.cmd("set script_path [ file dirname [ file normalize [ info script ] ] ]")
    tcl.cmd("puts $script_path")

    for w in wrapper_modules.values(): 
        tcl.cmd("cd $script_path")
        tcl.cmd(f"ipx::unload_core {w.desc.wrapper_xml_path}")
        tcl.cmd(f"source {w.desc.ipx_generate_script}")

    tcl.comment("INTEGRITY CHECKS")
        
    for w in wrapper_modules.values():
        tcl.cmd("cd $script_path")
        tcl.cmd(f"ipx::check_integrity [ipx::open_core {w.desc.wrapper_xml_path}]")
        tcl.cmd(f"ipx::unload_core")
        
    tcl.cmd("cd $prev_path")

    f = open("generate_all.tcl", "w")

    print(tcl.body, file=f)
    
    
def build_all():
    print("Building all...")
    build_libraries()
    
    build_interfaces()

    build_modules()

    wrap_modules()

    make_generate_all()
    
def deploy_file(src, dest):
    fpath = dest.joinpath(src)
    INFO(f"{src} => {fpath}")
    os.makedirs(fpath.parent, exist_ok=True)
    os.system(f"cp {src} {fpath}")

def clean_file(src, dest):
    fpath = dest.joinpath(src)
    INFO(f"clean {src} => rm {fpath}")
    os.makedirs(fpath.parent, exist_ok=True)
    os.system(f"rm {fpath}")
    

def deploy_libraries(dest):
    for lib in library_map.values():
        for fn in lib.files:
            deploy_file(Path(fn), dest)

        deploy_file(Path(lib.xml_path), dest)
    
def do_clean(dest):
    dest_path = Path(dest)
    INFO(f"Cleaning {dest}")

    clean_file(Path("library/component.xml"), dest_path)
    clean_file(Path("generate_all.tcl"), dest_path)
    
    for w in wrapper_modules.values():
        INFO(f"Deploying {w.name}...")
        clean_file(w.desc.ipx_generate_script, dest_path)
        clean_file(w.desc.wrapper_verilog_path, dest_path)
        clean_file(w.desc.wrapper_xgui_path, dest_path)
        clean_file(w.desc.wrapper_bd_tcl_path, dest_path)
    
    for w in wrapper_modules.values():
        INFO(f"Removing IP dir {dest_path.joinpath(w.desc.wrapper_path)}")
        os.system(f"rm -rf {dest_path.joinpath(w.desc.wrapper_path)}")
    
        
def do_deploy(dest):
    dest_path = Path(dest)
    INFO(f"Deploying to {dest}")

    deploy_libraries(dest_path)
    deploy_file(Path("generate_all.tcl"), dest_path)
    
    for w in wrapper_modules.values():
        INFO(f"Deploying {w.name}...")
        deploy_file(w.desc.ipx_generate_script, dest_path)
        deploy_file(w.desc.wrapper_verilog_path, dest_path)
        deploy_file(w.desc.wrapper_xgui_path, dest_path)
        deploy_file(w.desc.wrapper_bd_tcl_path, dest_path)
