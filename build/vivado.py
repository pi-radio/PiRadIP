from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys

from .piradip_build_base import *
from .bd import *

DEBUG=False

class TCLVivadoWrapper:
    def __init__(self):
        INFO("Launching background Vivado process")
        kwargs = {}

        if log_vivado:
           kwargs["logfile"] = sys.stdout
            
        self.p = pexpect.spawnu("vivado -nolog -nojournal -notrace -mode tcl", **kwargs)
        self.p.expect("Vivado%", timeout=60)

    def write(self, line, timeout=30):
        if line[0] == '#':
            return
        #print(line, end="")
        self.p.send(line)
        r = self.p.readline()

        if DEBUG:
            print(f"COMMAND: {line}")
            print(f"ECHO: {r}")
            
        retval = ""

        die = False
        
        while True:
            v = self.p.expect(["Vivado%", "INFO:.*\n", "ERROR:.*\n", "WARNING:.*\n"], timeout=timeout)

            if DEBUG:
                print(f"RESULT: {v} {self.p.after}")
            
            if v == 0:
                retval += self.p.before
                break
            elif v == 1:
                print(self.p.after.strip())
            elif v == 2:
                print(self.p.after.strip())
                print("DEATH!")
                die = True
            elif v == 3:
                print(self.p.after.strip())

        if die:
            print(f"Error Command: {line}")
            sys.exit(1)
                
        if DEBUG:
            print(f"RETVAL: {retval}")
        return retval.strip()

    def cmd(self, line, timeout=30):
        return self.write(f"{line}\n", timeout=timeout)

    def set_property(self, prop, val, obj):
        self.cmd(f"set_property -name \"{prop}\" -value \"{val}\" -objects {obj}")

def create_project(name):
    t = TCLVivadoWrapper()

    project_dir = Path.cwd()
    
    print(f"Creating project {name} in {project_dir}...")

    sources_dir = project_dir / "sources"
    
    constraints_dir = project_dir / "constraints"

    sources_dir.mkdir(exist_ok=True)
    constraints_dir.mkdir(exist_ok=True)

    constraints_file = constraints_dir / f"{name}.xdc"
    
    with open(constraints_file, "w") as f:
        pass

    wrapper_name = f"{name}_wrapper"
        
    class Project:
        def __init__(self, name, fpga, board):
            t.cmd(f"create_project -force {name}.xpr ./ -part {fpga}", timeout=90)
            self.set_property("board_part", board)

        def set_property(self, prop, val):
            t.set_property(prop, val, "[current_project]")

        def set_default_properties(self):
            self.set_property("default_lib", "xil_defaultlib")
            self.set_property("enable_resource_estimation", 0)
            self.set_property("enable_vhdl_2008", 1)
            self.set_property("ip_cache_permissions", "read write")
            self.set_property("ip_output_repo", f"ip_cache")
            self.set_property("mem.enable_memory_map_generation", "1")
            self.set_property("revised_directory_structure", "1")
            self.set_property("sim.central_dir", "ip_user_files")
            self.set_property("sim.ip.auto_export_scripts", "1")
            self.set_property("simulator_language", "Mixed")
            self.set_property("sim_compile_state", "1")
            self.set_property("webtalk.activehdl_export_sim", "49")
            self.set_property("webtalk.modelsim_export_sim", "49")
            self.set_property("webtalk.questa_export_sim", "49")
            self.set_property("webtalk.riviera_export_sim", "49")
            self.set_property("webtalk.vcs_export_sim", "49")
            self.set_property("webtalk.xsim_export_sim", "49")
            self.set_property("xpm_libraries", "XPM_CDC XPM_FIFO XPM_MEMORY")
            
    class ZCU111Project(Project):
        def __init__(self, name):
            super().__init__(name, "xczu28dr-ffvg1517-2-e", "xilinx.com:zcu111:part0:1.4")
            self.set_property("platform.board_id", "zcu111")

    class Fileset:
        def __init__(self, name, fstype="srcset"):
            self.name = name
            t.cmd(f"create_fileset -{fstype} {name}")

        def set_property(self, prop, val):
            t.set_property(prop, val, f"[get_filesets {self.name}]")

        def add_file(self, path):
            t.cmd(f"add_files -fileset {self.name} [list [file normalize \"{path}\"]]")
            
    p = ZCU111Project(name)
    p.set_default_properties

    f_sources = Fileset("sources")
    f_sources.set_property("ip_repo_paths", "[file normalize \"../PiRadIP\"]")

    t.cmd("update_ip_catalog -rebuild")

    f_sources.set_property("dataflow_viewer_settings", "min_width=16")
    f_sources.set_property("top", wrapper_name)

    f_constraints = Fileset("constraints", "constrset")

    f_constraints.add_file(constraints_file)

    f_simulations = Fileset("simulations", "simset")

    f_simulations.set_property("top", wrapper_name)
    f_simulations.set_property("top_lib", "xil_defaultlib")

    

    for ip in [ "xilinx.com:ip:proc_sys_reset:5.0",
                "xilinx.com:ip:xlconcat:2.1",
                "xilinx.com:ip:xlslice:1.0",
                "xilinx.com:ip:zynq_ultra_ps_e:3.4",
                "xilinx.com:ip:clk_wiz:6.0",
                "xilinx.com:ip:usp_rf_data_converter:2.6",
                "xilinx.com:ip:util_vector_logic:2.0",
                "pi-rad.io:piradip:axis_sample_buffer_in:1.0",
                "pi-rad.io:piradip:axis_sample_buffer_out:1.0",
                "pi-rad.io:piradip:axis_sample_interleaver:1.0",
                "pi-rad.io:piradip:piradip_slice32:1.0",
                "pi-rad.io:piradip:piradip_trigger_unit:1.0", ]:
        t.cmd(f"get_ipdefs -all {ip}")

            
    bd = BD(t, name)

    

    class SampleCapture(BDHier):
        def __init__(self, bd):
            super().__init__(bd, "data_capture")

            self.rfdc = RFDC(self, "rfdc")

            self.external_interfaces = list()
            self.external_clocks = list()
            
            print("Exporting physical RFDC interfaces")
            for p in self.rfdc.adc_clk + self.rfdc.dac_clk:
                np = BDIntfPin.construct(p.vlnv, self, p.name, p.mode)
                np.create()
                self.connect(np, p)
                self.external_interfaces.append(np)
                self.external_clocks.append(np)
                
            for p in self.rfdc.adc_in + self.rfdc.dac_out + [ self.rfdc.sysref_in ]:
                np = BDIntfPin.construct(p.vlnv, self, p.name, p.mode)
                np.create()
                self.connect(np, p)
                self.external_interfaces.append(np)

            BDPin(self, "ext_reset_in", pin_type="rst")
            BDPin(self, "irq", direction="O", pin_type="intr")
            BDPin(self, "s_axi_aclk", pin_type="clk")
            BDPin(self, "s_axi_aresetn", pin_type="rst")
                
            self.adc_axis_clocks = [
                ClockWizard(self, f"adc{i}_clk_wiz", [
                    ( "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ", "500.000" ),
                    ( "CONFIG.PRIM_IN_FREQ", "31.250" ),
                    ( "CONFIG.RESET_BOARD_INTERFACE", "Custom" ),
                    ( "CONFIG.USE_BOARD_FLOW", "true" )
                ]) for i in range(4) ]

                
        def get_rfdc_properties(self):
            prop = self.rfdc.list_properties().split()
            
            for p in prop:
                print(f"{p}: {self.rfdc.get_property(p)}")
            
            
    c = SampleCapture(bd)
    

    for p in c.external_interfaces:
        port = BDIntfPort.construct(p.vlnv, bd, p.name, mode=p.mode)
        #port = BDIntfPort(bd, p.name, mode=p.mode, vlnv=p.vlnv)
        port.create()
        if p in c.external_clocks:
            port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

        bd.connect(port, p)



    bd.validate()
    bd.save()
    bd.close()
    
    sys.exit(0)
    
    
    # Create the clocks


    dc_clocks = [ f"adc{i}_clk" for i in range(4) ] + [ f"dac{i}_clk" for i in range(2) ]
    dc_inputs = [ f"vin{i}_{p}" for i in range(4) for p in [ "01", "23" ] ]
    dc_outputs = [ f"vout{i}{p}" for i in range(2) for p in range(4) ]
        
    for clk in dc_clocks:
        create_clock(clk)
        
    t.cmd(f"set sysref_in [ create_bd_intf_port -mode Slave -vlnv xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0 sysref_in ]")

    for p in dc_inputs:
        create_intf_port("Slave", "xilinx.com:interface:diff_analog_io_rtl:1.0", p)

    for p in dc_outputs:
        create_intf_port("Master", "xilinx.com:interface:diff_analog_io_rtl:1.0", p)



    for clk in dc_clocks:
        create_intf_pin("Slave", "xilinx.com:interface:diff_clock_rtl:1.0", clk)

        
    create_intf_pin("Slave", "xilinx.com:interface:aximm_rtl:1.0", "s_axi")
    create_intf_pin("Slave", "xilinx.com:display_usp_rf_data_converter:diff_pins_rtl:1.0", "sysref_in")

    for p in dc_inputs:
        create_intf_pin("Slave", "xilinx.com:interface:diff_analog_io_rtl:1.0", p)

    for p in dc_outputs:
        create_intf_pin("Master", "xilinx.com:interface:diff_analog_io_rtl:1.0", p)


        
    create_pin("I", "rst", "ext_reset_in")
    create_pin("O", "intr", "irq_0")
    create_pin("I", "clk", "s_axi_aclk")
    create_pin("I", "rst", "s_axi_aresetn")
    
    clock_props = {
        "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": "500.000",
        "CONFIG.PRIM_IN_FREQ": "31.250",
        "CONFIG.RESET_BOARD_INTERFACE": "Custom",
        "CONFIG.USE_BOARD_FLOW": "true"
    }

        
    for i in range(4):
        bd.create_cell(f"adc{i}_clk_wiz", "xilinx.com:ip:clk_wiz:6.0", clock_props)
        bd.create_cell(f"adc{i}_rst", "xilinx.com:ip:proc_sys_reset:5.0")

    for i in range(2):
        bd.create_cell(f"dac{i}_rst", "xilinx.com:ip:proc_sys_reset:5.0")
        
    bd.create_cell(f"rfdc_rst", "xilinx.com:ip:proc_sys_reset:5.0")
        
    bd.create_cell(f"axi_interconnect_0", "xilinx.com:ip:axi_interconnect:2.1", { "CONFIG.NUM_MI": "34" })

    for i in range(8):
        bd.create_cell(f"axis_sample_buffer_in_{i}", "pi-rad.io:piradip:axis_sample_buffer_in:1.0", { "CONFIG.C_AXIMM_ADDR_WIDTH": "9", "CONFIG.STREAM_IN_WIDTH": "256" })

    for i in range(8):
        bd.create_cell(f"axis_sample_buffer_out_{i}", "pi-rad.io:piradip:axis_sample_buffer_out:1.0", { "CONFIG.C_AXIMM_ADDR_WIDTH": "14", "CONFIG.STREAM_OUT_WIDTH": "256" })

    for i in range(8):
        bd.create_cell(f"interleaver_{i}", "pi-rad.io:piradip:axis_sample_interleaver:1.0", { "CONFIG.IQ_OUT_WIDTH": "256", "CONFIG.I_IN_WIDTH": "128", "CONFIG.Q_IN_WIDTH": "128" })

    bd.create_cell("trigger_slice", "pi-rad.io:piradip:piradip_slice32:1.0")
    bd.create_cell("trigger_unit", "pi-rad.io:piradip:piradip_trigger_unit:1.0")

    rfdc_props = [
        ("CONFIG.ADC0_Multi_Tile_Sync", "true"),
        ("CONFIG.ADC0_Sampling_Rate", "4.0"),
        #("CONFIG.ADC1_Multi_Tile_Sync", "true"),
        #("CONFIG.ADC2_Multi_Tile_Sync", "true"),
        #("CONFIG.ADC3_Multi_Tile_Sync", "true"),
        #("CONFIG.ADC_Data_Type00", "1"),
        ("CONFIG.ADC_Data_Type02", "1"),
        #("CONFIG.ADC_Data_Type10", "1"),
        ("CONFIG.ADC_Data_Type12", "1"),
        ("CONFIG.ADC_Data_Type22", "1"),
        ("CONFIG.ADC_Data_Type32", "1"),
        ("CONFIG.ADC_Mixer_Mode00", "3"),
        ("CONFIG.ADC_Mixer_Mode02", "3"),
        ("CONFIG.ADC_Mixer_Mode10", "3"),
        ("CONFIG.ADC_Mixer_Mode12", "3"),
        ("CONFIG.ADC_Mixer_Mode20", "3"),
        ("CONFIG.ADC_Mixer_Mode22", "3"),
        ("CONFIG.ADC_Mixer_Mode30", "3"),
        ("CONFIG.ADC_Mixer_Mode32", "3"),
        ("CONFIG.ADC_Mixer_Type00", "2"),
        ("CONFIG.ADC_Mixer_Type02", "2"),
        ("CONFIG.ADC_Mixer_Type10", "2"),
        ("CONFIG.ADC_Mixer_Type12", "2"),
        ("CONFIG.ADC_Mixer_Type20", "2"),
        ("CONFIG.ADC_Mixer_Type22", "2"),
        ("CONFIG.ADC_Mixer_Type30", "2"),
        ("CONFIG.ADC_Mixer_Type32", "2"),
        ("CONFIG.ADC_Slice02_Enable", "true"),
        ("CONFIG.ADC_Slice10_Enable", "true"),
        ("CONFIG.ADC_Slice12_Enable", "true"),
        ("CONFIG.ADC_Slice20_Enable", "true"),
        ("CONFIG.ADC_Slice22_Enable", "true"),
        ("CONFIG.ADC_Slice30_Enable", "true"),
        ("CONFIG.ADC_Slice32_Enable", "true"),
        ("CONFIG.DAC0_Sampling_Rate", "4.0"),
        ("CONFIG.DAC1_Sampling_Rate", "4.0"),
        ("CONFIG.DAC_Mixer_Type00", "1"),
        ("CONFIG.DAC_Mixer_Type01", "1"),
        ("CONFIG.DAC_Mixer_Type02", "1"),
        ("CONFIG.DAC_Mixer_Type03", "1"),
        ("CONFIG.DAC_Mixer_Type10", "1"),
        ("CONFIG.DAC_Mixer_Type11", "1"),
        ("CONFIG.DAC_Mixer_Type12", "1"),
        ("CONFIG.DAC_Mixer_Type13", "1"),
        ("CONFIG.DAC_Slice00_Enable", "true"),
        ("CONFIG.DAC_Slice01_Enable", "true"),
        ("CONFIG.DAC_Slice02_Enable", "true"),
        ("CONFIG.DAC_Slice03_Enable", "true"),
        ("CONFIG.DAC_Slice10_Enable", "true"),
        ("CONFIG.DAC_Slice11_Enable", "true"),
        ("CONFIG.DAC_Slice12_Enable", "true"),
        ("CONFIG.DAC_Slice13_Enable", "true"),
    ]


    rfdc.list_properties()

    return
    

    
    bd.create_cell("not_0", "xilinx.com:ip:util_vector_logic:2.0", { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": "1" })

    for p in dc_outputs:
        bd.connect_iface(p, f"rfdc/{p}")

    for p in dc_inputs:
        bd.connect_iface(p, f"rfdc/{p}")

    for p in dc_clocks:
        bd.connect_iface(p, f"rfdc/{p}")

    bd.connect_iface("sysref_in", "rfdc/sysref_in")
        
    axi_i = 0

    class AXIInterconnect:
        def __init__(self, name, N):
            self.N = N
            self.n_connected = 0
            self.name = name

        def connect_master(self, other):
            bd.connect_iface(f"{self.name}/M{self.n_connected:02}_AXI", other)
            self.n_connected += 1

    ai = AXIInterconnect("axi_interconnect_0", 34)

    ai.connect_master("rfdc/s_axi")
    ai.connect_master("trigger_unit/AXILITE")

    for i in range(8):
        ai.connect_master(f"axis_sample_buffer_out_{i}/AXILITE")
        ai.connect_master(f"axis_sample_buffer_out_{i}/AXIMM")

    bd.connect_iface("s_axi", "axi_interconnect_0/S00_AXI")
    
        
    for i in range(8):
        ai.connect_master(f"axis_sample_buffer_in_{i}/AXILITE")
        ai.connect_master(f"axis_sample_buffer_in_{i}/AXIMM")
        
    for i, v in enumerate([ "00", "01", "02", "03", "10", "11", "12", "13" ]):
        print(v)
        bd.connect_iface(f"axis_sample_buffer_out_{i}/STREAM_OUT", f"rfdc/s{v}_axis")

    for i, (Ichan, Qchan) in enumerate([ ("00", "01"), ("02", "03"), ("10", "11"), ("12", "13"), ("20", "21"), ("22", "23"), ("30", "31"), ("32", "33") ]):
        bd.connect_iface(f"interleaver_{i}/I_IN", f"rfdc/m{Ichan}_axis")
        bd.connect_iface(f"interleaver_{i}/Q_IN", f"rfdc/m{Qchan}_axis")

    for i in range(8):
        bd.connect_iface(f"interleaver_{i}/IQ_OUT", f"axis_sample_buffer_in_{i}/STREAM_IN")

    for i in range(4):
        bd.connect_pins("adc{i}_clk_wiz/clk_out1", "interleaver_{2*i}/I_in_clk", "interleaver_{2*i}/Q_in_clk", "interleaver_{2*i+1}/I_in_clk", "interleaver_{2*i+1}/Q_in_clk")
        bd.connect_pins("adc{i}_clk_wiz/locked", "adc{i}_rst/dcm_locked")

    bd.connect_pins(*(["ext_reset_in"] + [ f"adc{i}_rst" for i in range(4) ] + [ f"dac{i}_rst" for i in range(2) ])) 
