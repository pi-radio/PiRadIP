#!/usr/bin/env python3

from build import *

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

axi4s_ports = [ 'tdata', 'tstrb', 'tlast', 'tvalid', 'tready' ]


add_interface("axi4mm",
              { 'file': "library/aximm/piradip_aximm.sv",
                'parameters': {
                    'ADDR_WIDTH': {
                        'description': "Width of the address bus"
                    },
                    'STRB_WIDTH': {
                        'description': "Width of the strobe field"
                    }
                },
                'ipxdesc': {
                    "memoryMapped": True,
                    "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm", 'version': "1.0" },
                    "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm_rtl", 'version': "1.0" },
                    "ports":  axi4mm_ports,
                    "port_map": upper_map(axi4mm_ports),
                    "clock": { 'name': "clk" },
                    "reset": { 'name': "resetn", 'polarity': 'low' }
                }
              })

"""
        parameter integer DATA_WIDTH    = 32,
		parameter integer ID_WIDTH  	= 1,
        parameter integer AWUSER_WIDTH	= 0,
		parameter integer ARUSER_WIDTH	= 0,
		parameter integer WUSER_WIDTH	= 0,
		parameter integer RUSER_WIDTH	= 0,
		parameter integer BUSER_WIDTH	= 0,
                   parameter integer STRB_WIDTH = (DATA_WIDTH/8)
"""
                
add_interface("axi4mm_lite",
              {
                  'file': "library/aximm/piradip_axi4mmlite.sv",
                  'parameters': {
                      'ADDR_WIDTH': {
                          'description': "Width of the address bus"
                      },
                      'STRB_WIDTH': {
                          'description': "Width of the strobe field"
                      }
                  },
                  'ipxdesc': {
                      "memoryMapped": True,
                      "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm", 'version': "1.0" },
                      "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "aximm_rtl", 'version': "1.0" },
                      "ports":  axi4mm_lite_ports,
                      "port_map": upper_map(axi4mm_lite_ports),
                      "clock": { 'name': "clk" },
                      "reset": { 'name': "resetn", 'polarity': 'low' }
                  }
              }
)

add_interface("axi4s",
              {
                  'file': "library/axis/piradip_axis.sv",
                  'ipxdesc': {
                      "memoryMapped": False,
                      "busType": { 'vendor': "xilinx.com", 'library': "interface", 'name': "axis", 'version': "1.0" },
                      "abstractionType":  { 'vendor': "xilinx.com", 'library': "interface", 'name': "axis_rtl", 'version': "1.0" },
                      "ports":  axi4s_ports,
                      "port_map": upper_map(axi4s_ports),
                      "clock": { 'name': "clk" },
                      "reset": { 'name': "resetn", 'polarity': 'low' }
                  }
              }
)

add_module("piradip_axis_sample_buffer_out",
           "library/axis/piradip_axis_sample_buffer_out.sv",
           wrapper_name="AXIS_SampleBufferOut",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="AXI Sample Buffer Out")

add_module("piradspi",
           "library/spi/piradspi.sv",
           wrapper_name="piradspi_ip",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="PiRadSPI")


build_all()
