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

class UCSB_Capture(BD):
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

        print("Using AXI SPI...")
                    
        self.axi_spi = AXI_SPI(self, "spi", { "CONFIG.C_NUM_SS_BITS": 29, "CONFIG.Multiples16": 2 })
        
        self.axi_spi.pins["ext_spi_clk"].connect(self.ps.pl_clk[0])
        
        self.axi_interconnect.aximm.connect(self.axi_spi.pins["AXI_LITE"])
        
        self.miso = self.reexport(self.axi_spi.pins["io1_i"])
        self.mosi = self.reexport(self.axi_spi.pins["io0_o"])
        self.sclk = self.reexport(self.axi_spi.pins["sck_o"])

        self.slice16 = Slice16(self, "csn_slice", None)

        print(self.slice16.pins)        

        self.LTC5586_CSN = [ self.reexport(self.slice16.pins[f"dout{n}"], name=f"LTC5586_{n}_CSN") for n in range(8) ]
        self.RX_PWR_LEFT_CS = self.reexport(self.slice16.pins["dout8"], name="RX_PWR_LEFT_CS")
        self.RX_PWR_RIGHT_CS = self.reexport(self.slice16.pins["dout9"], name="RX_PWR_RIGHT_CS")
        self.TX_PWR_LEFT_CS = self.reexport(self.slice16.pins["dout10"], name="TX_PWR_LEFT_CS")
        self.TX_PWR_RIGHT_CS = self.reexport(self.slice16.pins["dout11"], name="TX_PWR_RIGHT_CS")
        self.LMX_ERAVANT_CS = self.reexport(self.slice16.pins["dout12"], name="LMX_ERAVANT_CS")
        self.LMX_RX_CS = self.reexport(self.slice16.pins["dout13"], name="LMX_RX_CS")
        self.LMX_TX_CS = self.reexport(self.slice16.pins["dout14"], name="LMX_TX_CS")
        
        self.connect(self.axi_spi.pins["ss_o"], self.slice16.pins["din"])

        self.gpio = GPIO(self, "pl_gpio")

        self.axi_interconnect.aximm.connect(self.gpio.pins["S_AXI"])

        self.gpio_slice32 = Slice32(self, "gpio_slice", None)

        self.connect(self.gpio.pins["gpio_io_o"], self.gpio_slice32.pins["din"])

        self.CTRL_EREVANT_RX = self.reexport(self.gpio_slice32.pins["dout0"])
        self.CTRL_EREVANT_TX = self.reexport(self.gpio_slice32.pins["dout1"])
        
        self.capture = SampleCapture(self)

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])
                
        self.ps.connect_interrupts()

        # "C6", "A6", "B5", "A9", "A7", "C5", "A10", "A5"
        for p, loc in zip(self.LTC5586_CSN, [ RFMC.DAC.IO_07.Ball, RFMC.DAC.IO_02.Ball,
                                              RFMC.DAC.IO_05.Ball, RFMC.DAC.IO_00.Ball,
                                              RFMC.DAC.IO_03.Ball, RFMC.DAC.IO_06.Ball,
                                              RFMC.DAC.IO_01.Ball, RFMC.DAC.IO_04.Ball ]):
            print(f"Mapping {p} to {loc}")
            p.set_phys(loc)

        self.miso.set_phys("B8")
        self.mosi.set_phys("B7")
        self.sclk.set_phys("B10")
            
        self.RX_PWR_LEFT_CS.set_phys(RFMC.ADC.IO_00.Ball) # AP5
        self.RX_PWR_RIGHT_CS.set_phys(RFMC.ADC.IO_01.Ball) # AP6
        self.TX_PWR_LEFT_CS.set_phys("C10")
        self.TX_PWR_RIGHT_CS.set_phys("D10")
        self.LMX_ERAVANT_CS.set_phys("C7")
        self.LMX_RX_CS.set_phys("D9")
        self.LMX_TX_CS.set_phys("D8")

        self.CTRL_EREVANT_RX.set_phys(RFMC.ADC.IO_04.Ball) # AV7
        self.CTRL_EREVANT_TX.set_phys(RFMC.ADC.IO_03.Ball) # AR7
