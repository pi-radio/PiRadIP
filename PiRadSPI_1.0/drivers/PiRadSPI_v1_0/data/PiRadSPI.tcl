

proc generate {drv_handle} {
	xdefine_include_file $drv_handle "xparameters.h" "PiRadSPI" "NUM_INSTANCES" "DEVICE_ID"  "C_CSR_BASEADDR" "C_CSR_HIGHADDR"
}
