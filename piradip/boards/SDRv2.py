from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import os.path
from pathlib import Path
import pexpect
import functools
import sys
from functools import cached_property

from piradip.vivado.bd import *

class SDRv2_Capture(BD):
    def __init__(self, t, name):
        super().__init__(t, name)


        print("Creating Zynq UltraScale(TM) Processing System cell...")
                
        self.ps = Zynq_US_PS(self, "ps")

        self.ps.setup_aximm()


        
        print("Creating AXI Interconnect...")

        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2, num_managers=3,
                                                global_clock=self.ps.aximm_clocks[0],
                                                global_reset=self.ps.aximm_clocks[0].assoc_resetn)

        self.ps.pl_clk[0].connect(self.axi_interconnect.pins["ACLK"])
        self.ps.pl_clk[0].assoc_resetn.connect(self.axi_interconnect.pins["ARESETN"])
        
        self.axi_interconnect.pins["S00_AXI"].connect(self.ps.pins["M_AXI_HPM0_FPD"])
        self.axi_interconnect.pins["S01_AXI"].connect(self.ps.pins["M_AXI_HPM1_FPD"])
        
        print("Creating i2c for clock tree...")
                
        self.i2c_clk = BDI2C(self, "i2c_clk", None)

        i2c_clk_pin = self.i2c_clk.pins["IIC"]

        #i2c_clk_pin.dump_pins()
        
        i2c_clk_port = self.reexport(self.i2c_clk.pins["IIC"], name="IIC_CLK")

        i2c_clk_port.sda_out.set_phys(RFMC.ADC.IO_15.Ball, "LVCMOS18")
        i2c_clk_port.scl_out.set_phys(RFMC.ADC.IO_17.Ball, "LVCMOS18")
        
        self.axi_interconnect.aximm.connect(self.i2c_clk.pins["S_AXI"])
        
        print("Creating SPI...")
        
        self.spi = PiRadSPI(self, "spi", {"CONFIG.C_SPI_SEL_WIDTH": 6})

        #self.spi.dump_properties()
        #self.spi.dump_pins()

        self.axi_interconnect.aximm.connect(self.spi.pins["CSR"])
        self.ps.pl_clk[0].connect(self.spi.pins["io_clk"])

        miso = self.reexport(self.spi.pins["miso"])
        mosi = self.reexport(self.spi.pins["mosi"])
        sclk = self.reexport(self.spi.pins["sclk"])
        csn = self.reexport(self.spi.pins["csn"])

        csn[0].set_phys(RFMC.DAC.IO_04.Ball, "LVCMOS18")
        csn[1].set_phys(RFMC.DAC.IO_06.Ball, "LVCMOS18")
        csn[2].set_phys(RFMC.DAC.IO_09.Ball, "LVCMOS18")
        csn[3].set_phys(RFMC.DAC.IO_00.Ball, "LVCMOS18")
        csn[4].set_phys(RFMC.DAC.IO_02.Ball, "LVCMOS18")
        csn[5].set_phys(RFMC.DAC.IO_17.Ball, "LVCMOS18")
        
        miso.set_phys(RFMC.DAC.IO_03.Ball, "LVCMOS18")
        mosi.set_phys(RFMC.DAC.IO_05.Ball, "LVCMOS18")
        sclk.set_phys(RFMC.DAC.IO_01.Ball, "LVCMOS18")
        
        self.capture = SampleCapture(self)

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

        #self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])

        self.ps.connect_interrupts()
