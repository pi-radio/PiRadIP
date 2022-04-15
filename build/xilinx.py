from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from .ipxact_base import NS_XILINX

import ipxact2009

def xilinx_list():
    return field(default_factory=list, metadata={ "namespace": NS_XILINX })

def xilinx_attr():
    return field(metadata = { 'type': "Attribute", 'namespace': NS_XILINX })

def xilinx_optional():
    return field(default=None)

class XMeta:
    namespace = NS_XILINX

@dataclass
class CoreExtensions:
    """
    Core extensions for component
    """
    class Meta(XMeta):
        name = "coreExtensions"

    @dataclass
    class XPMLibraries:
        """
        XPM library list
        """
        class Meta(XMeta):
            name = "xpmLibraries"

        @dataclass
        class XPMLibrary:
            """
            XPM Library Reference
            """
            class Meta(XMeta):
                name = "xpmLibrary"

            value: str
            
        xpmLibrary: List[XPMLibrary] = xilinx_list()

        
    @dataclass
    class Taxonomies:
        """
        Taxonomy list
        """
        class Meta(XMeta):
            name = "taxonomies"

        @dataclass
        class Taxonomy:
            """
            IP Taxonomy
            """
            class Meta:
                name = "taxonomy"
                namespace = NS_XILINX
                
            value: str
        
        taxonomy: List[Taxonomy] = xilinx_list()

    @dataclass
    class SupportedFamilies:
        """
        Supported Silicon Families
        """
        class Meta(XMeta):
            name = "supportedFamilies"

        @dataclass
        class Family:
            """
            Silicon Family
            """
            class Meta(XMeta):
                name = "family"

            lifeCycle: str = xilinx_attr()
            value: str

        familiy: List[Family] = xilinx_list()
        
    taxonomies: Taxonomies
    displayName: Optional[str]
    supportedFamilies: Optional[SupportedFamilies] = field(default=None)
    hideInCatalogGUI: Optional[bool] = field(default=None)
    xpmLibraries: XPMLibraries = field(default=None)
    vendorDisplayName: Optional[str] = field(default=None)
    vendorURL: Optional[str] = field(default=None)
    coreRevision: Optional[int] = field(default=None)
    coreCreationDateTime: Optional[str] = field(default=None)

@dataclass
class SubCoreRef:
    """
    Reference to another core
    """
    class Meta:
        name = "subCoreRef"
        namespace = NS_XILINX

    @dataclass
    class ComponentRef:
        """
        Component Reference
        """
        class Meta:
            name = "componentRef"
            namespace = NS_XILINX

        @dataclass
        class Mode:
            """
            Reference Mode
            """
            class Meta:
                name = "mode"
                namespace = NS_XILINX

            name: str = field(metadata={ 'type': "Attribute", 'namespace': NS_XILINX })

            
        vendor: str = field(metadata={ 'type': "Attribute", 'namespace': NS_XILINX })
        library: str = field(metadata={ 'type': "Attribute", 'namespace': NS_XILINX })
        name: str = field(metadata={ 'type': "Attribute", 'namespace': NS_XILINX })
        version: str = field(metadata={ 'type': "Attribute", 'namespace': NS_XILINX })
        mode: Mode = field(metadata={ 'namespace': NS_XILINX })
        
    componentRef: ComponentRef = field(metadata={ 'namespace': NS_XILINX })
    
    
def get_subcore_reference():
    return ipxact2009.FileSet(
        name="xilinx_anylanguagesynthesis_pi_rad_io_piradip_piradip_1_0__ref_view_fileset",
        vendor_extensions=ipxact2009.VendorExtensions(
            SubCoreRef(
                SubCoreRef.ComponentRef(
                    vendor="pi-rad.io", library="piradip", name="piradip", version="1.0",
                    mode=SubCoreRef.ComponentRef.Mode(name="copy_mode")
                )
            )
        )
    )
    

    
template_xgui_tcl = """
# Definitional proc to organize widgets for parameters.
proc init_gui { IPINST } {
  ipgui::add_param $IPINST -name "Component_Name"
  #Adding Page
  set Page_0 [ipgui::add_page $IPINST -name "Page 0"]
  ipgui::add_param $IPINST -name "C_S01_AXI_ID_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_DATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_S01_AXI_ADDR_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_AWUSER_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_ARUSER_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_WUSER_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_RUSER_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_BUSER_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_BASEADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S01_AXI_HIGHADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S00_AXI_DATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_S00_AXI_ADDR_WIDTH" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S00_AXI_BASEADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_S00_AXI_HIGHADDR" -parent ${Page_0}
  ipgui::add_param $IPINST -name "C_M00_AXIS_TDATA_WIDTH" -parent ${Page_0} -widget comboBox
  ipgui::add_param $IPINST -name "C_M00_AXIS_START_COUNT" -parent ${Page_0}


}

proc update_PARAM_VALUE.C_S01_AXI_ID_WIDTH { PARAM_VALUE.C_S01_AXI_ID_WIDTH } {
	# Procedure called to update C_S01_AXI_ID_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_ID_WIDTH { PARAM_VALUE.C_S01_AXI_ID_WIDTH } {
	# Procedure called to validate C_S01_AXI_ID_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_DATA_WIDTH { PARAM_VALUE.C_S01_AXI_DATA_WIDTH } {
	# Procedure called to update C_S01_AXI_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_DATA_WIDTH { PARAM_VALUE.C_S01_AXI_DATA_WIDTH } {
	# Procedure called to validate C_S01_AXI_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_ADDR_WIDTH { PARAM_VALUE.C_S01_AXI_ADDR_WIDTH } {
	# Procedure called to update C_S01_AXI_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_ADDR_WIDTH { PARAM_VALUE.C_S01_AXI_ADDR_WIDTH } {
	# Procedure called to validate C_S01_AXI_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH { PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH } {
	# Procedure called to update C_S01_AXI_AWUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH { PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH } {
	# Procedure called to validate C_S01_AXI_AWUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH { PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH } {
	# Procedure called to update C_S01_AXI_ARUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH { PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH } {
	# Procedure called to validate C_S01_AXI_ARUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_WUSER_WIDTH { PARAM_VALUE.C_S01_AXI_WUSER_WIDTH } {
	# Procedure called to update C_S01_AXI_WUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_WUSER_WIDTH { PARAM_VALUE.C_S01_AXI_WUSER_WIDTH } {
	# Procedure called to validate C_S01_AXI_WUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_RUSER_WIDTH { PARAM_VALUE.C_S01_AXI_RUSER_WIDTH } {
	# Procedure called to update C_S01_AXI_RUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_RUSER_WIDTH { PARAM_VALUE.C_S01_AXI_RUSER_WIDTH } {
	# Procedure called to validate C_S01_AXI_RUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_BUSER_WIDTH { PARAM_VALUE.C_S01_AXI_BUSER_WIDTH } {
	# Procedure called to update C_S01_AXI_BUSER_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_BUSER_WIDTH { PARAM_VALUE.C_S01_AXI_BUSER_WIDTH } {
	# Procedure called to validate C_S01_AXI_BUSER_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_BASEADDR { PARAM_VALUE.C_S01_AXI_BASEADDR } {
	# Procedure called to update C_S01_AXI_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_BASEADDR { PARAM_VALUE.C_S01_AXI_BASEADDR } {
	# Procedure called to validate C_S01_AXI_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_S01_AXI_HIGHADDR { PARAM_VALUE.C_S01_AXI_HIGHADDR } {
	# Procedure called to update C_S01_AXI_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S01_AXI_HIGHADDR { PARAM_VALUE.C_S01_AXI_HIGHADDR } {
	# Procedure called to validate C_S01_AXI_HIGHADDR
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_DATA_WIDTH { PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to update C_S00_AXI_DATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_DATA_WIDTH { PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to validate C_S00_AXI_DATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_ADDR_WIDTH { PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to update C_S00_AXI_ADDR_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_ADDR_WIDTH { PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to validate C_S00_AXI_ADDR_WIDTH
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_BASEADDR { PARAM_VALUE.C_S00_AXI_BASEADDR } {
	# Procedure called to update C_S00_AXI_BASEADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_BASEADDR { PARAM_VALUE.C_S00_AXI_BASEADDR } {
	# Procedure called to validate C_S00_AXI_BASEADDR
	return true
}

proc update_PARAM_VALUE.C_S00_AXI_HIGHADDR { PARAM_VALUE.C_S00_AXI_HIGHADDR } {
	# Procedure called to update C_S00_AXI_HIGHADDR when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_S00_AXI_HIGHADDR { PARAM_VALUE.C_S00_AXI_HIGHADDR } {
	# Procedure called to validate C_S00_AXI_HIGHADDR
	return true
}

proc update_PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH { PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH } {
	# Procedure called to update C_M00_AXIS_TDATA_WIDTH when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH { PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH } {
	# Procedure called to validate C_M00_AXIS_TDATA_WIDTH
	return true
}

proc update_PARAM_VALUE.C_M00_AXIS_START_COUNT { PARAM_VALUE.C_M00_AXIS_START_COUNT } {
	# Procedure called to update C_M00_AXIS_START_COUNT when any of the dependent parameters in the arguments change
}

proc validate_PARAM_VALUE.C_M00_AXIS_START_COUNT { PARAM_VALUE.C_M00_AXIS_START_COUNT } {
	# Procedure called to validate C_M00_AXIS_START_COUNT
	return true
}


proc update_MODELPARAM_VALUE.C_S01_AXI_ID_WIDTH { MODELPARAM_VALUE.C_S01_AXI_ID_WIDTH PARAM_VALUE.C_S01_AXI_ID_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_ID_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_ID_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_DATA_WIDTH { MODELPARAM_VALUE.C_S01_AXI_DATA_WIDTH PARAM_VALUE.C_S01_AXI_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_DATA_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_ADDR_WIDTH { MODELPARAM_VALUE.C_S01_AXI_ADDR_WIDTH PARAM_VALUE.C_S01_AXI_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_AWUSER_WIDTH { MODELPARAM_VALUE.C_S01_AXI_AWUSER_WIDTH PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_AWUSER_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_AWUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_ARUSER_WIDTH { MODELPARAM_VALUE.C_S01_AXI_ARUSER_WIDTH PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_ARUSER_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_ARUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_WUSER_WIDTH { MODELPARAM_VALUE.C_S01_AXI_WUSER_WIDTH PARAM_VALUE.C_S01_AXI_WUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_WUSER_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_WUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_RUSER_WIDTH { MODELPARAM_VALUE.C_S01_AXI_RUSER_WIDTH PARAM_VALUE.C_S01_AXI_RUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_RUSER_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_RUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S01_AXI_BUSER_WIDTH { MODELPARAM_VALUE.C_S01_AXI_BUSER_WIDTH PARAM_VALUE.C_S01_AXI_BUSER_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S01_AXI_BUSER_WIDTH}] ${MODELPARAM_VALUE.C_S01_AXI_BUSER_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH { MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH PARAM_VALUE.C_S00_AXI_DATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S00_AXI_DATA_WIDTH}] ${MODELPARAM_VALUE.C_S00_AXI_DATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH { MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH PARAM_VALUE.C_S00_AXI_ADDR_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_S00_AXI_ADDR_WIDTH}] ${MODELPARAM_VALUE.C_S00_AXI_ADDR_WIDTH}
}

proc update_MODELPARAM_VALUE.C_M00_AXIS_TDATA_WIDTH { MODELPARAM_VALUE.C_M00_AXIS_TDATA_WIDTH PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_M00_AXIS_TDATA_WIDTH}] ${MODELPARAM_VALUE.C_M00_AXIS_TDATA_WIDTH}
}

proc update_MODELPARAM_VALUE.C_M00_AXIS_START_COUNT { MODELPARAM_VALUE.C_M00_AXIS_START_COUNT PARAM_VALUE.C_M00_AXIS_START_COUNT } {
	# Procedure called to set VHDL generic/Verilog parameter value(s) based on TCL parameter value
	set_property value [get_property value ${PARAM_VALUE.C_M00_AXIS_START_COUNT}] ${MODELPARAM_VALUE.C_M00_AXIS_START_COUNT}
}


"""

template_bd_tcl = """
proc init { cellpath otherInfo } {                                                                   
                                                                                                             
	set cell_handle [get_bd_cells $cellpath]                                                                 
	set all_busif [get_bd_intf_pins $cellpath/*]		                                                     
	set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]
	set full_sbusif_list [list  S01_AXI ]
			                                                                                                 
	foreach busif $all_busif {                                                                               
		if { [string equal -nocase [get_property MODE $busif] "slave"] == 1 } {                            
			set busif_param_list [list]                                                                      
			set busif_name [get_property NAME $busif]					                                     
			if { [lsearch -exact -nocase $full_sbusif_list $busif_name ] == -1 } {					         
			    continue                                                                                     
			}                                                                                                
			foreach tparam $axi_standard_param_list {                                                        
				lappend busif_param_list "C_${busif_name}_${tparam}"                                       
			}                                                                                                
			bd::mark_propagate_only $cell_handle $busif_param_list			                                 
		}		                                                                                             
	}                                                                                                        
}


proc pre_propagate {cellpath otherInfo } {                                                           
                                                                                                             
	set cell_handle [get_bd_cells $cellpath]                                                                 
	set all_busif [get_bd_intf_pins $cellpath/*]		                                                     
	set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]
	                                                                                                         
	foreach busif $all_busif {	                                                                             
		if { [string equal -nocase [get_property CONFIG.PROTOCOL $busif] "AXI4"] != 1 } {                  
			continue                                                                                         
		}                                                                                                    
		if { [string equal -nocase [get_property MODE $busif] "master"] != 1 } {                           
			continue                                                                                         
		}			                                                                                         
		                                                                                                     
		set busif_name [get_property NAME $busif]			                                                 
		foreach tparam $axi_standard_param_list {		                                                     
			set busif_param_name "C_${busif_name}_${tparam}"			                                     
			                                                                                                 
			set val_on_cell_intf_pin [get_property CONFIG.${tparam} $busif]                                  
			set val_on_cell [get_property CONFIG.${busif_param_name} $cell_handle]                           
			                                                                                                 
			if { [string equal -nocase $val_on_cell_intf_pin $val_on_cell] != 1 } {                          
				if { $val_on_cell != "" } {                                                                  
					set_property CONFIG.${tparam} $val_on_cell $busif                                        
				}                                                                                            
			}			                                                                                     
		}		                                                                                             
	}                                                                                                        
}


proc propagate {cellpath otherInfo } {                                                               
                                                                                                             
	set cell_handle [get_bd_cells $cellpath]                                                                 
	set all_busif [get_bd_intf_pins $cellpath/*]		                                                     
	set axi_standard_param_list [list ID_WIDTH AWUSER_WIDTH ARUSER_WIDTH WUSER_WIDTH RUSER_WIDTH BUSER_WIDTH]
	                                                                                                         
	foreach busif $all_busif {                                                                               
		if { [string equal -nocase [get_property CONFIG.PROTOCOL $busif] "AXI4"] != 1 } {                  
			continue                                                                                         
		}                                                                                                    
		if { [string equal -nocase [get_property MODE $busif] "slave"] != 1 } {                            
			continue                                                                                         
		}			                                                                                         
	                                                                                                         
		set busif_name [get_property NAME $busif]		                                                     
		foreach tparam $axi_standard_param_list {			                                                 
			set busif_param_name "C_${busif_name}_${tparam}"			                                     
                                                                                                             
			set val_on_cell_intf_pin [get_property CONFIG.${tparam} $busif]                                  
			set val_on_cell [get_property CONFIG.${busif_param_name} $cell_handle]                           
			                                                                                                 
			if { [string equal -nocase $val_on_cell_intf_pin $val_on_cell] != 1 } {                          
				#override property of bd_interface_net to bd_cell -- only for slaves.  May check for supported values..
				if { $val_on_cell_intf_pin != "" } {                                                         
					set_property CONFIG.${busif_param_name} $val_on_cell_intf_pin $cell_handle               
				}                                                                                            
			}                                                                                                
		}		                                                                                             
	}                                                                                                        
}
"""
