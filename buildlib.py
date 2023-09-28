#!/usr/bin/env python3

from piradip import *

import click

Library("piradlib",
        path="library/",
        vlnv=VLNV("pi-rad.io", "library", "PiRadIP", "1.0"),
        description="Pi Radio IP Library",
        files = [
            "library/axi/piradip_axi4.svh",
            "library/axis/piradip_axis.svh",
            
            "library/util/piradip_latency_synchronizer.sv",
            "library/util/piradip_state_timer.sv",
            "library/util/piradip_tb_shift_registers.sv",
            "library/util/piradip_shift_registers.sv",
            "library/util/piradip_shifters.sv",
            "library/util/piradip_slice.sv",
            "library/util/piradip_concat.sv",
            
            "library/aximm/piradip_axi4.sv",
            "library/aximm/piradip_axi4mmlite.sv",
            "library/aximm/piradip_aximm.sv",
            "library/aximm/piradip_register_if.sv",

            "library/axis/piradip_axis.sv",
        
            "library/fifo/piradip_sync_fifo.sv",
            
            "library/axis/piradip_axis_fifo.sv",
            
            "library/mem/piradip_dual_port_ram.sv",
            "library/cdc/piradip_cdc.sv",
            
            "library/mem/piradip_axi4_ram_adapter.sv",
        
            "library/axis/piradip_axis_sample_buffer.sv",
            "library/axis/piradip_axis_sample_buffer_out.sv",
            "library/axis/piradip_axis_sample_buffer_in.sv",
            "library/axis/piradip_axis_sample_interleaver.sv",
            "library/axis/piradip_axis_gain_block.sv",

            "library/util/piradip_trigger_unit.sv",
            
            "library/spi/piradspi_pkg.sv",
            "library/spi/piradspi_cmd_fifo.sv",
            "library/spi/piradspi_csr.sv",
            "library/spi/piradspi_engine.sv",
            "library/spi/piradspi.sv",
])
        
def upper_map(l):
    return dict([ (i, i.upper()) for i in l ])

axi4mm_lite_ports = [ 'awaddr', 'awprot', 'awvalid', 'awready', 'wdata', 'wstrb', 'wvalid', 'wready',
                      'bresp', 'bvalid', 'bready', 'araddr', 'arprot', 'arvalid', 'arready',
                      'rdata', 'rresp', 'rvalid', 'rready' ]

axi4mm_ports = [ 'awid', 'awaddr', 'awlen', 'awsize', 'awburst',
                 'awlock', 'awcache', 'awprot', 'awregion', 'awqos', 'awuser',
                 'awvalid', 'awready', 'wdata', 'wstrb', 'wlast', 'wuser', 'wvalid',
                 'wready', 'bid', 'bresp', 'buser', 'bvalid', 'bready',
                 'arid', 'araddr', 'arlen', 'arsize', 'arburst', 'arlock',
                 'arcache', 'arprot', 'arregion', 'arqos', 'aruser',
                 'arvalid', 'arready', 'rid', 'rdata', 'rresp', 'rlast',
                 'ruser', 'rvalid', 'rready' ]

axi4s_ports = [ 'tdata', 'tstrb', 'tlast', 'tvalid', 'tready', 'tkeep', 'tid', 'tdest', 'tuser' ]


InterfaceDesc(
    name="axi4mm",
    file="library/aximm/piradip_aximm.sv",
    parameters = [
        ParameterDesc('ADDR_WIDTH', "Width of the address busses", prefix="C_"),
        ParameterDesc('DATA_WIDTH', "Width of the data buses", allowed_values=[ 32, 64 ], prefix="C_"),
        ParameterDesc('ID_WIDTH', "Width of the id busses", prefix="C_"),
        ParameterDesc('AWUSER_WIDTH', "Width of the write address user bus", prefix="C_"),
        ParameterDesc('ARUSER_WIDTH', "Width of the read address user bus", prefix="C_"),
        ParameterDesc('WUSER_WIDTH', "Width of the write user bus", prefix="C_"),
        ParameterDesc('RUSER_WIDTH', "Width of the read user bus", prefix="C_"),
        ParameterDesc('BUSER_WIDTH', "Width of the write response user bus", prefix="C_"),
        ParameterDesc('ID_WIDTH', "Width of the ID busses", prefix="C_")        
    ],
    ipxdesc = IPXDesc(
        busType = VLNV("xilinx.com", "interface", "aximm", "1.0"),
        abstractionType = VLNV("xilinx.com", "interface", "aximm_rtl", "1.0"),
        ports = axi4mm_ports,
        port_map = upper_map(axi4mm_ports),
        clock = IPXClock("clk"),
        reset = IPXReset("resetn", "low"),
        memoryMapped = True,
        mmtype = "mem",
        xilinxParameters = [
            IPXParameterDesc('WIZ_DATA_WIDTH', "DATA Bus Width", [ "32" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.WIZ_DATA_WIDTH",
                             default_value="32"),
            IPXParameterDesc('WIZ_MEMORY_SIZE', "Memory size", [ "4096" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.WIZ_MEMORY_SIZE",
                             default_value="4096"),
            IPXParameterDesc('SUPPORTS_NARROW_BURST', "Narrow burst support", [ "0", "1" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.SUPPORTS_NARROW_BURST",
                             default_value="1")
            
            ]
    )
)

InterfaceDesc(
    name="axi4mm_lite",
    file="library/aximm/piradip_axi4mmlite.sv",
    parameters = [
        ParameterDesc('ADDR_WIDTH', "Width of the address busses", prefix="C_"),
        ParameterDesc('DATA_WIDTH', "Width of the data buses", allowed_values=[32], prefix="C_"),
        ParameterDesc('ID_WIDTH', "Width of the id busses", prefix="C_"),
        ParameterDesc('AWUSER_WIDTH', "Width of the write address user bus", prefix="C_"),
        ParameterDesc('ARUSER_WIDTH', "Width of the read address user bus", prefix="C_"),
        ParameterDesc('WUSER_WIDTH', "Width of the write user bus", prefix="C_"),
        ParameterDesc('RUSER_WIDTH', "Width of the read user bus", prefix="C_"),
        ParameterDesc('BUSER_WIDTH', "Width of the write response user bus", prefix="C_")
    ],
    ipxdesc = IPXDesc(
        busType = VLNV("xilinx.com", "interface", "aximm", "1.0"),
        abstractionType = VLNV("xilinx.com", "interface", "aximm_rtl", "1.0"),
        ports = axi4mm_lite_ports,
        port_map = upper_map(axi4mm_lite_ports),
        clock = IPXClock("clk"),
        reset = IPXReset("resetn", "low"),
        memoryMapped = True,
        mmtype = "reg",
        xilinxParameters = [
            IPXParameterDesc('WIZ_DATA_WIDTH', "DATA Bus Width", [ "32" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.WIZ_DATA_WIDTH",
                             default_value="32"),
            IPXParameterDesc('WIZ_MEMORY_SIZE', "Memory size", [ "4096" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.WIZ_MEMORY_SIZE",
                             default_value="4096"),
            IPXParameterDesc('SUPPORTS_NARROW_BURST', "Narrow burst support", [ "0", "1" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.SUPPORTS_NARROW_BURST",
                             default_value="1")
            
            ]        
    )
)

InterfaceDesc(
    name="axi4s",
    file="library/axis/piradip_axis.sv",
    parameters = [],
    ipxdesc = IPXDesc(
        busType = VLNV("xilinx.com", "interface", "axis", "1.0"),
        abstractionType = VLNV("xilinx.com", "interface", "axis_rtl", "1.0" ),
        ports = axi4s_ports,
        port_map = upper_map(axi4s_ports),
        clock = IPXClock("clk"),
        reset = IPXReset("resetn", "low"),
        xilinxParameters = [
            IPXParameterDesc('WIZ_DATA_WIDTH', "DATA Bus Width", [ "32", "64", "128", "256" ],
                             usage="all",
                             ipxact_id="BUSIFPARAM_VALUE.{i.busname}.WIZ_DATA_WIDTH",
                             default_value="32"),            
            ]
        )
)

ModuleDesc(name="piradip_axis_gain_block",
           version="1.0",
           file="library/axis/piradip_axis_gain_block.sv",
           wrapper_name="AXIS_GainBlock",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="AXI Gain Block",
           ipxact_name="axis_gain_block"
)

ModuleDesc(name="piradip_axis_sample_buffer_out",
           version="1.0",
           file="library/axis/piradip_axis_sample_buffer_out.sv",
           wrapper_name="AXIS_SampleBufferOut",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="AXI Sample Buffer Out",
           ipxact_name="axis_sample_buffer_out"
)

ModuleDesc(name="piradip_axis_sample_buffer_in",
           version="1.0",
           file="library/axis/piradip_axis_sample_buffer_in.sv",
           wrapper_name="AXIS_SampleBufferIn",
           description="A memory mapped sample buffer to capture streamed data",
           display_name="AXI Sample Buffer In",
           ipxact_name="axis_sample_buffer_in"
)

ModuleDesc(name="piradip_axis_sample_interleaver",
           version="1.0",
           file="library/axis/piradip_axis_sample_interleaver.sv",
           wrapper_name="AXIS_SampleInterleaver",
           description="A memory mapped sample buffer to capture streamed data",
           display_name="AXI Sample Interleaver",
           ipxact_name="axis_sample_interleaver"
)


ModuleDesc(name="piradip_trigger_unit",
           version="1.0",
           file="library/util/piradip_trigger_unit.sv",
           wrapper_name="piradip_trigger_unit_ip",
           description="A unit to coordinate triggers across mulitple other units",
           display_name="AXI Trigger Unit w/ Delay",
           ipxact_name="piradip_trigger_unit"
)

ModuleDesc(name="piradspi",
           version="1.0",
           file="library/spi/piradspi.sv",
           wrapper_name="piradspi_ip",
           description="A very flexible SPI controller",
           display_name="PiRadSPI",
           ipxact_name="piradspi_ip"
)

ModuleDesc(name="piradip_slice8",
           version="1.0",
           file="library/util/piradip_slice.sv",
           wrapper_name="piradip_slice8_ip",
           description="Slice 8 bits individually",
           display_name="PiRadIP Slice 8",
           ipxact_name="piradip_slice8"
)

ModuleDesc(name="piradip_slice16",
           version="1.0",
           file="library/util/piradip_slice.sv",
           wrapper_name="piradip_slice16_ip",
           description="Slice 16 bits individually",
           display_name="PiRadIP Slice 16",
           ipxact_name="piradip_slice16"
)

ModuleDesc(name="piradip_slice32",
           version="1.0",
           file="library/util/piradip_slice.sv",
           wrapper_name="piradip_slice32_ip",
           description="Slice 8 bits individually",
           display_name="PiRadIP Slice 32",
           ipxact_name="piradip_slice32"
)

ModuleDesc(name="piradip_concat8",
           version="1.0",
           file="library/util/piradip_concat.sv",
           wrapper_name="piradip_concat8_ip",
           description="Concat 8 bits together",
           display_name="PiRadIP Concat 8",
           ipxact_name="piradip_concat8"
)

ModuleDesc(name="piradip_concat16",
           version="1.0",
           file="library/util/piradip_concat.sv",
           wrapper_name="piradip_concat16_ip",
           description="Concat 16 bits together",
           display_name="PiRadIP Concat 16",
           ipxact_name="piradip_concat16"
)

ModuleDesc(name="piradip_concat32",
           version="1.0",
           file="library/util/piradip_concat.sv",
           wrapper_name="piradip_concat32_ip",
           description="Concat 32 bits individually",
           display_name="PiRadIP Concat 32",
           ipxact_name="piradip_concat32"
)



@click.group(chain=True)
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    pass

@cli.command('reformat')
def reformat():
    reformat_all()

@cli.command('lint')
def lint():
    lint_all()
    
@cli.command('build')
def build():
    build_all()

@cli.command('deploy')
@click.argument('destination')
def deploy(destination):
    do_deploy(destination)

@cli.command('cleandeploy')
@click.argument('destination')
def cleandeploy(destination):
    do_clean(destination)
    do_deploy(destination)

if __name__ == '__main__':
    cli()
    
