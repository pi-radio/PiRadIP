from .piradip_build_base import *

from .structure import library_map, VLNV

from .ipxact_base import *
"""
from .ipxact_node import *
from .ipxact_bus import *
from .ipxact_collection import *
"""
from .ipxact_component import *
from .xilinx import *
from .sv import *

import io
import datetime
import os
import time

from .ipx import *
    
library_rev=str(int(time.time()))

class IPXACTLibrary(IPXACTComponent2):
    def __init__(self, desc):
        self.desc = desc
        self.library_path = os.path.join(os.getcwd(), "library")

        super(IPXACTLibrary, self).__init__(desc.vlnv, desc.description)
        
        relpaths = [ os.path.relpath(i, self.library_path) for i in self.desc.files ]

        self.synthesis_fs.file = [ ipxact_file(fn) for fn in relpaths ]
        
        self.simulation_fs.file = [ ipxact_file(fn) for fn in relpaths ]
                
        self.component.parameters = ipxact2009.Parameters()
        self.component.parameters.parameter = [
            ipxact2009.Parameter(name="Component_Name",
                                 value=ipxact2009.NameValuePairType.Value(
                                     value = "PiRadIP_v1_0",
                                     resolve="user",
                                     id="PARAM_VALUE.Component_Name",
                                     order=1
                                 )
            ) ]

        self.component.vendor_extensions = ipxact2009.VendorExtensions(
            any_element=CoreExtensions(
                taxonomies=CoreExtensions.Taxonomies( [
                    "/BaseIP",
                    "/Embedded_Processing/AXI_Infrastructure",
                    "/Memories_&_Storage_Elements"
                ] ),
                displayName="Pi Radio IP Library v1.0",
                hideInCatalogGUI=True,
                xpmLibraries=CoreExtensions.XPMLibraries(
                    [ CoreExtensions.XPMLibraries.XPMLibrary(i) for i in ["XPM_CDC", "XPM_FIFO", "XPM_MEMORY"]]
                ),
                vendorURL="https://pi-rad.io/",
                vendorDisplayName="Pi Radio Inc.",
                coreRevision=library_rev
            )
        )

    def xml_file(self, mode):
        return open(self.desc.xml_path, mode)

            
