from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys
from functools import cached_property

from .piradip_build_base import *
from .bd import *

class SDRv2_Capture(BD):
    def __init__(self, t, name):
        super().__init__(t, name)


        print("Creating Zynq UltraScale(TM) Processing System cell...")
                
        self.ps = Zynq_US_PS(self, "ps")

        self.ps.setup_aximm()


        
        print("Creating AXI Interconnect...")

        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2, num_managers=4,
                                                global_clock=self.ps.aximm_clocks[0],
                                                global_reset=self.ps.aximm_clocks[0].assoc_resetn)

        self.ps.pl_clk[0].connect(self.axi_interconnect.pins["ACLK"])
        self.ps.pl_clk[0].assoc_resetn.connect(self.axi_interconnect.pins["ARESETN"])
        

        
        print("Creating i2c for clock tree...")
                
        self.i2c_clk = BDI2C(self, "i2c_clk", None)

        self.reexport(self.i2c_clk.pins["IIC"], name="IIC_CLK")
        
        self.i2c_clk.dump_pins()

        self.axi_interconnect.aximm.connect(self.i2c_clk.pins["S_AXI"])

        
        print("Creating i2c for SIVERS radios...")

        self.i2c_radios = BDI2C(self, "i2c_radios", None)

        self.reexport(self.i2c_radios.pins["IIC"], name="IIC_RADIOS")
        
        self.axi_interconnect.aximm.connect(self.i2c_radios.pins["S_AXI"])


        
        print("Creating SPI...")
        
        self.spi = PiRadSPI(self, "spi", None)

        self.spi.dump_pins()

        self.axi_interconnect.aximm.connect(self.spi.pins["CSR"])
        self.ps.pl_clk[0].connect(self.spi.pins["io_clk"])

        self.reexport(self.spi.pins["miso"])
        self.reexport(self.spi.pins["mosi"])
        self.reexport(self.spi.pins["sclk"])
        
        
        self.capture = SampleCapture(self)

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

        self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])
