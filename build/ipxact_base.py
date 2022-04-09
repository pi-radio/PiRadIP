import sys

from lxml import etree
from lxml.builder import ElementMaker

NS_XILINX="http://www.xilinx.com"
NS_SPIRIT="http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009"
#xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"

S = ElementMaker(namespace = NS_SPIRIT,
                 nsmap = { 'spirit': NS_SPIRIT, 'xilinx': NS_XILINX });

X = ElementMaker(namespace = NS_XILINX,
                 nsmap = { 'xilinx': NS_XILINX });


class VLNV:
    def __init__(self, vendor="xilinx.com", library="signal", name="dookie", version="1.0"):
        self.vendor = vendor
        self.library = library
        self.name = name
        self.version = version
        
