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

add_interface("axi4mm", "library/aximm/piradip_aximm.sv")
add_interface("axi4mm_lite", "library/aximm/piradip_axi4mmlite.sv")
add_interface("axi4s", "library/axis/piradip_axis.sv")

add_module("piradip_axis_sample_buffer_out",
           "library/axis/piradip_axis_sample_buffer_out.sv",
           wrapper_name="AXIS_SampleBufferOut",
           description="A memory mapped sample buffer to stream out over an AXI stream interface",
           display_name="AXI Sample Buffer Out")

build_all()
