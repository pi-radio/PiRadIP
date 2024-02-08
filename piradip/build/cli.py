import os
import sys
import click
import pathlib
from pathlib import Path
import shutil
import importlib

from piradip.vivado import PiRadioProject

@click.group(chain=True)
@click.option('-d', '--build-dir', 'build_dir', default=None)
@click.pass_context
def cli(ctx, build_dir):
    if build_dir is None:
        p = Path.cwd()
    else:
        p = Path(build_dir)
        os.chdir(p)
        
    if (p / "bitstream.py").exists():
        print(f"Loading board definition from {p}/board.py...")
        m = importlib.import_module("bitstream")

        class project(PiRadioProject):
            bd_template = m.bitstream_definition
            project_name = bd_template.bitstream_name


            
        ctx.obj = project
    elif (p / "library.py").exists():
        pass
    else:
        print("No board or library files found...")

def do_clean(prj):
    here = Path(".")

    l = here.glob(f"{prj.project_name}.*")

    for p in l:
        print(f"Removing {p}...")
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()

    f = (here / "checkpoints").glob("*.dcp")

    for p in f:
        p.unlink()

    if (here/"ip_cache").exists():
        shutil.rmtree(here/"ip_cache")

@cli.command()
@click.pass_context
def clean(ctx):
    prj = ctx.obj()
    do_clean(prj)

@cli.command()
@click.pass_context
def create(ctx):
    prj = ctx.obj()
    do_clean(prj)
    prj.create()

@cli.command()
@click.pass_context
def generate(ctx):
    prj = ctx.obj()

    prj.vivado.cmd(f"open_project {prj.project_name}")
    prj.vivado.cmd(f"update_compile_order -fileset sources_1")
    prj.vivado.cmd(f"open_bd_design {prj.bd_path}")


    prj.vivado.cmd(f"generate_target -force -verbose all [get_files {prj.bd_path}]", timeout=15*60)
    prj.vivado.cmd(f"export_ip_user_files -of_objects [get_files {prj.bd_path}] -no_script -sync -force -quiet", timeout=15*60)
    prj.vivado.cmd(f"export_simulation -of_objects [get_files {prj.bd_path}]"
                   + f" -directory ip_user_files/sim_scripts"
                   + f" -ip_user_files_dir ip_user_files"
                   + f" -ipstatic_source_dir BetelgeuseNRT.ip_user_files/ipstatic"
                   + f" -lib_map_path [list {{modelsim=cache/compile_simlib/modelsim}}"
                   + f"  {{questa=cache/compile_simlib/questa}}"
                   + f"  {{xcelium=cache/compile_simlib/xcelium}}"
                   + f"  {{vcs=cache/compile_simlib/vcs}}"
                   + f"  {{riviera=cache/compile_simlib/riviera}}]"
                   + f" -use_ip_compiled_libs -force -quiet",
                   timeout=15*60)


@cli.command("create-runs")
@click.pass_context
def create_runs(ctx):
    prj = ctx.obj()

    prj.open()
    
    prj.create_runs()
    
@cli.command("ip-status")
@click.pass_context
def ip_status(ctx):
    prj = ctx.obj()

    prj.vivado.cmd(f"open_project {prj.project_name}")

    prj.vivado.cmd(f"open_bd_design {prj.bd_path}")

    print(prj.vivado.cmd(f"report_ip_status"))
    
@cli.command("upgrade-ip")
@click.pass_context
def upgrade_ip(ctx):
    prj = ctx.obj()

    npm = prj.NPM

    npm.load_bd(locked_ok=True)

    npm.check_ips()
        
@cli.command()
@click.pass_context
def synthesize(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.synthesize()
    
@cli.command()
@click.pass_context
def optimize(ctx, checkpoint):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.optimize()

@cli.command()
@click.pass_context
def place(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.place()

@cli.command()
@click.pass_context
def route(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.route()

@cli.command("write-bitstream")
@click.pass_context
def write_bitstream(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.write_bitstream()

@cli.command("write-xsa")
@click.pass_context
def write_xsa(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.write_xsa()

@cli.command("write-bin")
@click.pass_context
def write_bin(ctx):
    prj = ctx.obj()

    #open non-project mode
    npm = prj.NPM

    npm.write_bin()

    
@cli.command("dtbo")
@click.pass_context
def dtbo(ctx):
    prj = ctx.obj()
 
    #open non-project mode
    npm = prj.NPM

    npm.dtbo()

@cli.command("iplib")
@click.pass_context
def iplib(ctx):
    p = Path(__file__).parent.parent.parent.resolve()
    
    if os.system(f"cd {p}; ./buildlib.py build") != 0:
        raise RuntimeError("Failed to build IP lib")
    
    
    
@cli.command("import-run")
@click.pass_context
def import_run(ctx):
    prj = ctx.obj()
    
    os.system(f"cp {prj.project_name}.runs/synth_1/{prj.project_name}_wrapper.dcp checkpoints/synthesize.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_opt.dcp checkpoints/optimize.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_placed.dcp checkpoints/place.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_routed.dcp checkpoints/route.dcp")
    
    pass

@cli.command()
@click.pass_context
def info(ctx):
    print("Info")

@cli.command()
@click.pass_context
def half_monty(ctx):
    ctx.invoke(create)
    ctx.invoke(generate)
    ctx.invoke(synthesize)
    ctx.invoke(dtbo)
    
@cli.command()
@click.pass_context
def full_monty(ctx):
    ctx.invoke(iplib)
    ctx.invoke(half_monty)

