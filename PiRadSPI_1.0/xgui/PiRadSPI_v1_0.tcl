# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  ipgui::add_param $IPINST -name "C_SPI_SEL_MODE"
  ipgui::add_param $IPINST -name "C_CSR_DATA_WIDTH"
  ipgui::add_param $IPINST -name "C_CSR_ADDR_WIDTH"
  ipgui::add_param $IPINST -name "C_SPI_SEL_WIDTH"
  ipgui::add_param $IPINST -name "C_NUM_PROFILES"

}

proc update_PARAM_VALUE.C_CSR_ADDR_WIDTH { PARAM_VALUE.C_CSR_ADDR_WIDTH } {
	# Procedure called to update C_CSR_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_CSR_ADDR_WIDTH { PARAM_VALUE.C_CSR_ADDR_WIDTH } {
	# Procedure called to validate C_CSR_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_CSR_DATA_WIDTH { PARAM_VALUE.C_CSR_DATA_WIDTH } {
	# Procedure called to update C_CSR_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_CSR_DATA_WIDTH { PARAM_VALUE.C_CSR_DATA_WIDTH } {
	# Procedure called to validate C_CSR_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_NUM_PROFILES { PARAM_VALUE.C_NUM_PROFILES } {
	# Procedure called to update C_NUM_PROFILES when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_NUM_PROFILES { PARAM_VALUE.C_NUM_PROFILES } {
	# Procedure called to validate C_NUM_PROFILES
	return true
}

proc update_PARAM_VALUE.C_SPI_SEL_MODE { PARAM_VALUE.C_SPI_SEL_MODE } {
	# Procedure called to update C_SPI_SEL_MODE when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_SPI_SEL_MODE { PARAM_VALUE.C_SPI_SEL_MODE } {
	# Procedure called to validate C_SPI_SEL_MODE
	return true
}

proc update_PARAM_VALUE.C_SPI_SEL_WIDTH { PARAM_VALUE.C_SPI_SEL_WIDTH } {
	# Procedure called to update C_SPI_SEL_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_SPI_SEL_WIDTH { PARAM_VALUE.C_SPI_SEL_WIDTH } {
	# Procedure called to validate C_SPI_SEL_WIDTH
	return true
}


proc update_MODELPARAM_VALUE.C_SPI_SEL_MODE { MODELPARAM_VALUE.C_SPI_SEL_MODE PARAM_VALUE.C_SPI_SEL_MODE } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_SPI_SEL_MODE}] ${MODELPARAM_VALUE.C_SPI_SEL_MODE}
}

proc update_MODELPARAM_VALUE.C_CSR_DATA_WIDTH { MODELPARAM_VALUE.C_CSR_DATA_WIDTH PARAM_VALUE.C_CSR_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_CSR_DATA_WIDTH}] ${MODELPARAM_VALUE.C_CSR_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_CSR_ADDR_WIDTH { MODELPARAM_VALUE.C_CSR_ADDR_WIDTH PARAM_VALUE.C_CSR_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_CSR_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_CSR_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.C_SPI_SEL_WIDTH { MODELPARAM_VALUE.C_SPI_SEL_WIDTH PARAM_VALUE.C_SPI_SEL_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_SPI_SEL_WIDTH}] ${MODELPARAM_VALUE.C_SPI_SEL_WIDTH}
}

proc update_MODELPARAM_VALUE.C_NUM_PROFILES { MODELPARAM_VALUE.C_NUM_PROFILES PARAM_VALUE.C_NUM_PROFILES } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_NUM_PROFILES}] ${MODELPARAM_VALUE.C_NUM_PROFILES}
}

