
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


TEST_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_DIR=$(join $(realpath $(TEST_DIR)/../../), /)

VSOURCES=$(addprefix $(ROOT_DIR), $(SOURCES))


all: elaborate
	echo $(ROOT_DIR)

glbl.v: ${RDI_APPROOT}/data/verilog/src/glbl.v
	cp $< $@

xvlog.pb: $(VSOURCES) glbl.v Makefile
	xvlog --work work --sv $(VSOURCES) glbl.v

compile: xvlog.pb

xelab.pb: compile
	xelab --debug all -L xpm -top $(TOP_MODULE) -snapshot test_snapshot glbl

elaborate: xelab.pb

simulate: elaborate
	xsim -R test_snapshot

gui: elaborate
	xsim --gui test_snapshot --view test_snapshot.wcfg
