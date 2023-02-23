import os
import sys
import click
from pathlib import Path
import shutil

@click.group(chain=True)
@click.pass_context
def cli(ctx):
    pass
    
@cli.command()
@click.pass_context
def create(ctx):
    prj = ctx.obj()
    prj.create()

@cli.command()
@click.pass_context
def generate(ctx):
    prj = ctx.obj()

    prj.vivado.cmd(f"open_project {prj.project_name}")

    prj.vivado.cmd(f"open_bd_design {prj.bd_path}")

    prj.vivado.cmd(f"generate_target -force -verbose all [get_files {prj.bd_path}]")

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

    npm.load_bd()

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
    if os.system("cd ../PiRadIP; ./buildlib.py build") != 0:
        raise RuntimeError("Failed to build IP lib")
    
    
@cli.command()
@click.pass_context
def clean(ctx):
    prj = ctx.obj()

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
    
    
@cli.command("import-run")
@click.pass_context
def import_run(ctx):
    prj = ctx.obj()
    
    os.system(f"cp {prj.project_name}.runs/synth_1/{prj.project_name}_wrapper.dcp checkpoints/synthesize.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_opt.dcp checkpoints/optimize.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_placed.dcp checkpoints/place.dcp")
    os.system(f"cp {prj.project_name}.runs/impl_1/{prj.project_name}_wrapper_routed.dcp checkpoints/route.dcp")
    
    pass


    
    
