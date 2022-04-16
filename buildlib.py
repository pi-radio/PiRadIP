#!/usr/bin/env python3

from build import *

import click



add_library_file("library/axis/piradip_axis_sample_buffer_out.sv")
add_library_file("library/axis/piradip_axis.sv")
add_library_file("library/axis/piradip_axis_fifo.sv")
add_library_file("library/axis/piradip_axis_sample_buffer_in.sv")
add_library_file("library/mem/piradip_axi4_ram_adapter.sv")
add_library_file("library/mem/piradip_dual_port_ram.sv")
add_library_file("library/util/piradip_latency_synchronizer.sv")
add_library_file("library/util/piradip_state_timer.sv")
add_library_file("library/util/piradip_tb_shift_registers.sv")
add_library_file("library/util/piradip_shift_registers.sv")
add_library_file("library/util/piradip_shifters.sv")
add_library_file("library/aximm/piradip_axi4mmlite.sv")
add_library_file("library/aximm/piradip_aximm.sv")
add_library_file("library/fifo/piradip_sync_fifo.sv")
add_library_file("library/cdc/piradip_cdc.sv")


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
        ParameterDesc('ADDR_WIDTH', "Width of the address busses"),
        ParameterDesc('DATA_WIDTH', "Width of the data buses", allowed_values=[ 32, 64 ]),
        ParameterDesc('ID_WIDTH', "Width of the id busses"),
        ParameterDesc('AWUSER_WIDTH', "Width of the write address user bus"),
        ParameterDesc('ARUSER_WIDTH', "Width of the read address user bus"),
        ParameterDesc('WUSER_WIDTH', "Width of the write user bus"),
        ParameterDesc('RUSER_WIDTH', "Width of the read user bus"),
        ParameterDesc('BUSER_WIDTH', "Width of the write response user bus")
    ],
    ipxdesc = IPXDesc(
        busType = VLNV("xilinx.com", "interface", "aximm", "1.0"),
        abstractionType = VLNV("xilinx.com", "interface", "aximm_rtl", "1.0"),
        ports = axi4mm_ports,
        port_map = upper_map(axi4mm_ports),
        clock = IPXClock("clk"),
        reset = IPXReset("resetn", "low"),
        memoryMapped = True,
        mmtype = "mem"
    )
)

InterfaceDesc(
    name="axi4mm_lite",
    file="library/aximm/piradip_axi4mmlite.sv",
    parameters = [
        ParameterDesc('ADDR_WIDTH', "Width of the address busses"),
        ParameterDesc('DATA_WIDTH', "Width of the data buses", allowed_values=[32]),
        ParameterDesc('ID_WIDTH', "Width of the id busses"),
        ParameterDesc('AWUSER_WIDTH', "Width of the write address user bus"),
        ParameterDesc('ARUSER_WIDTH', "Width of the read address user bus"),
        ParameterDesc('WUSER_WIDTH', "Width of the write user bus"),
        ParameterDesc('RUSER_WIDTH', "Width of the read user bus"),
        ParameterDesc('BUSER_WIDTH', "Width of the write response user bus")
    ],
    ipxdesc = IPXDesc(
        busType = VLNV("xilinx.com", "interface", "aximm", "1.0"),
        abstractionType = VLNV("xilinx.com", "interface", "aximm_rtl", "1.0"),
        ports = axi4mm_lite_ports,
        port_map = upper_map(axi4mm_lite_ports),
        clock = IPXClock("clk"),
        reset = IPXReset("resetn", "low"),
        memoryMapped = True,
        mmtype = "reg"
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
        )
)

ModuleDesc(name="piradip_axis_sample_buffer_out",
           version="1.0",
           file="library/axis/piradip_axis_sample_buffer_out.sv",
           wrapper_name="AXIS_SampleBufferOut",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="AXI Sample Buffer Out",
           ipxact_name="axis_sample_buffer_out"
)

#ModuleDesc(name="piradip_axis_sample_buffer_in",
#           version="1.0",
#           file="library/axis/piradip_axis_sample_buffer_out.sv",
#           wrapper_name="AXIS_SampleBufferOut",
#           description="A memory mapped sample buffer to stream out over an AXI stream interface",
#           display_name="AXI Sample Buffer Out",
#           ipxact_name="axis_sample_buffer_out"
#)


ModuleDesc(name="piradspi",
           version="1.0",
           file="library/spi/piradspi.sv",
           wrapper_name="piradspi_ip",
           description="A very flexible SPI controller",
           display_name="PiRadSPI",
           ipxact_name="piradspi_ip"
)


@click.group(chain=True)
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    print("CLI")

@cli.command('build')
def build():
    build_all()

@cli.command('deploy')
@click.argument('destination')
def deploy(destination):
    do_deploy(destination)
    


if __name__ == '__main__':
    cli()
    
