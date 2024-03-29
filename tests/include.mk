TEST_DIR=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ROOT_DIR=$(join $(realpath $(TEST_DIR)/../../), /)

VSOURCES=$(addprefix $(ROOT_DIR), $(SOURCES))


all: elaborate
	echo $(ROOT_DIR)

../glbl.v: ${XILINX_VIVADO}/data/verilog/src/glbl.v
	cp $< $@

xvlog.pb: $(VSOURCES) ../glbl.v Makefile ../include.mk
	xvlog --work work --include ../../library/axi --sv $(VSOURCES) ../glbl.v

compile: xvlog.pb

xelab.pb: compile
	xelab -initfile=/opt/Xilinx/Vivado/2022.2/data/xsim/ip/xsim_ip.ini --debug all -L UNISIMS_VER -L UNIMACRO_VER -L xpm -top $(TOP_MODULE) -snapshot test_snapshot glbl

elaborate: xelab.pb

simulate: elaborate
	xsim -R test_snapshot

gui: elaborate
	xsim --gui test_snapshot --view test_snapshot.wcfg

lint: $(VSOURCES) 
	verible-verilog-lint $(VSOURCES)
