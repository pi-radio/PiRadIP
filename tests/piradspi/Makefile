
SOURCES=
#SOURCES+=../../../opt/Xilinx/Vivado/2021.2/data/xsim/ip/xpm/xpm_fifo_axis.sdb
SOURCES+=library/fifo/piradip_sync_fifo.sv

SOURCES+=library/axis/piradip_axis.sv
SOURCES+=library/axis/piradip_axis_fifo.sv
SOURCES+=library/aximm/piradip_axi4.sv
SOURCES+=library/aximm/piradip_axi4mmlite.sv
SOURCES+=library/aximm/piradip_register_if.sv


SOURCES+=library/util/piradip_state_timer.sv
SOURCES+=library/util/piradip_shift_registers.sv

SOURCES+=library/spi/piradspi_pkg.sv


SOURCES+=library/spi/piradspi_cmd_fifo.sv
SOURCES+=library/spi/piradspi_engine.sv
SOURCES+=library/spi/piradspi_csr.sv

SOURCES+=library/spi/piradspi.sv

SOURCES+=piradspi_ip/hdl/piradspi_ip_1.0.sv

SOURCES+=tb/util/piradip_tb_clocks.sv
SOURCES+=tb/aximm/piradip_tb_aximm_util.sv
SOURCES+=tb/aximm/piradip_tb_aximm_manager.sv
SOURCES+=tb/spi/piradip_tb_spi_device.sv
SOURCES+=tb/spi/piradspi_tb_full.sv

TOP_MODULE=piradspi_tb_full

include ../include.mk

