import sys

from lxml import etree
from lxml.builder import ElementMaker

NS_XILINX="http://www.xilinx.com"
NS_SPIRIT="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"
#xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

ns_map = { 'spirit': NS_SPIRIT, 'xilinx': NS_XILINX }

from pathlib import PurePath, Path
import pprint
import ipxact2009
from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.formats.dataclass.serializers import XmlSerializer
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.parsers.handlers import LxmlEventHandler

S = ElementMaker(namespace = NS_SPIRIT,
                 nsmap = { 'spirit': NS_SPIRIT, 'xilinx': NS_XILINX });

X = ElementMaker(namespace = NS_XILINX,
                 nsmap = { 'xilinx': NS_XILINX });


def dump_xml(node):
    print(etree.tostring(node).decode())

                
def ipxact_file(fn):
    f = ipxact2009.File();

    f.name = str(fn)

    ext = PurePath(fn).suffix

    if ext == ".sv":
        f.file_type = ipxact2009.FileFileType.SYSTEM_VERILOG_SOURCE
    elif ext == ".svh":
        f.file_type = ipxact2009.FileFileType.SYSTEM_VERILOG_SOURCE
        f.is_include_file = True
    elif ext == ".tcl":
        f.file_type = ipxact2009.FileFileType.TCL_SOURCE
    else:
        WARN(f"Unknown file type for extension {ext}")
    
    return f
