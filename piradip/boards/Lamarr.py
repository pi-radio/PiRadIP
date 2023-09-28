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

class Lamarr_Capture(BD):
    def __init__(self, t, name):
        super().__init__(t, name)

        print("Creating Zynq UltraScale(TM) Processing System cell...")
                
        self.ps = Zynq_US_PS(self, "ps")

        self.ps.setup_aximm()

        print("Creating AXI Interconnect...")

        self.axi_interconnect = AXIInterconnect(self, "axi_interconnect",
                                                num_subordinates=2, num_managers=2,
                                                global_clock=self.ps.aximm_clocks[0],
                                                global_reset=self.ps.aximm_clocks[0].assoc_resetn)

        self.ps.pl_clk[0].connect(self.axi_interconnect.pins["ACLK"])
        self.ps.pl_clk[0].assoc_resetn.connect(self.axi_interconnect.pins["ARESETN"])
        
        self.axi_interconnect.pins["S00_AXI"].connect(self.ps.pins["M_AXI_HPM0_FPD"])
        self.axi_interconnect.pins["S01_AXI"].connect(self.ps.pins["M_AXI_HPM1_FPD"])

        self.capture = SampleCapture(self)

        for p in self.capture.external_interfaces:
            port = self.reexport(p)
            if p in self.capture.external_clocks:
                port.set_property_list([("CONFIG.FREQ_HZ", "4000000000.0")])

                
        #self.capture.dump_pins()

        self.axi_interconnect.aximm.connect(self.capture.pins["S00_AXI"])
        self.ps.pl_resetn[0].connect(self.capture.pins["ext_reset_in"])


        self.gpio = GPIO(self, "pl_gpio")
        self.concat32 = Concat32(self, "gpio_concat", None)
        self.slice32 = Slice32(self, "gpio_slice", None)
        
        self.axi_interconnect.aximm.connect(self.gpio.pins["S_AXI"])
        
        self.connect(self.gpio.pins["gpio_io_o"], self.slice32.pins["din"])
        self.connect(self.gpio.pins["gpio_io_i"], self.concat32.pins["dout"])
        
        self.obs_ctrl = self.reexport(self.slice32.pins["dout0"])

        self.obs_ctrl.set_phys(RFMC.ADC.IO_19.Ball, "LVCMOS18")

        # We're using SPI gpio for now because of the truly f$#$ed HMC630x read protocol
        # I mean, who thought that was a good idea?
        
        """
        self.axi_spi = AXI_SPI(self, "spi", { "CONFIG.C_NUM_SS_BITS": 25, "CONFIG.Multiples16": 2 })
        """
        
        csn_names = (
            [ f"RX_CS{i}" for i in range(8) ] +
            [ f"TX_CS{i}" for i in range(8) ] +
            [ f"LTC5586_CS{i}" for i in range(8) ] +
            [ "LMX_CS" ]
        )
        
        spi_csns = [
            # RX Chip Selects
            RFMC.ADC.IO_07.Ball, RFMC.ADC.IO_02.Ball, RFMC.ADC.IO_05.Ball, RFMC.ADC.IO_00.Ball,
            RFMC.ADC.IO_03.Ball, RFMC.ADC.IO_06.Ball, RFMC.ADC.IO_01.Ball, RFMC.ADC.IO_04.Ball,
            # TX Chip Selects
            RFMC.DAC.IO_07.Ball, RFMC.DAC.IO_02.Ball, RFMC.DAC.IO_05.Ball, RFMC.DAC.IO_00.Ball,
            RFMC.DAC.IO_03.Ball, RFMC.DAC.IO_01.Ball, RFMC.DAC.IO_04.Ball, RFMC.DAC.IO_06.Ball,
            # LTC5586 Chip Selects
            RFMC.DAC.IO_10.Ball, RFMC.DAC.IO_11.Ball, RFMC.DAC.IO_12.Ball, RFMC.DAC.IO_13.Ball,
            RFMC.DAC.IO_14.Ball, RFMC.DAC.IO_15.Ball, RFMC.DAC.IO_16.Ball, RFMC.DAC.IO_17.Ball,
            # LMX CS
            RFMC.ADC.IO_11.Ball
        ]

        self.miso = self.reexport(self.concat32.pins["din1"])
        self.mosi = self.reexport(self.slice32.pins["dout2"])
        self.sclk = self.reexport(self.slice32.pins["dout3"])
        self.miso_1v8 = self.reexport(self.concat32.pins["din30"])

        self.miso.set_phys(RFMC.DAC.IO_08.Ball, "LVCMOS18")
        self.mosi.set_phys(RFMC.ADC.IO_12.Ball, "LVCMOS18")
        self.sclk.set_phys(RFMC.ADC.IO_10.Ball, "LVCMOS18")
        self.miso_1v8.set_phys(RFMC.DAC.IO_19.Ball, "LVCMOS18")

        
        for i, (ball, name) in enumerate(zip(spi_csns, csn_names)):
            cs = self.reexport(self.slice32.pins[f"dout{i+4}"], name=name)
            cs.set_phys(ball, "LVCMOS18")
        

        """
        self.csn_slice = Slice32(self, "csn_slice", None);
        
        self.axi_spi.pins["ss_o"].connect(self.csn_slice.pins["din"])

        for i, v in enumerate(spi_csns):
            p = self.reexport(self.csn_slice.pins[f"dout{i}"], name=csn_names[i])
            p.set_phys(v, "LVCMOS18")
            
        self.miso = self.reexport(self.axi_spi.pins["io1_i"])
        self.mosi = self.reexport(self.axi_spi.pins["io0_o"])
        self.sclk = self.reexport(self.axi_spi.pins["sck_o"])

        self.miso.set_phys(RFMC.DAC.IO_08.Ball, "LVCMOS18")
        self.mosi.set_phys(RFMC.ADC.IO_12.Ball, "LVCMOS18")
        self.sclk.set_phys(RFMC.ADC.IO_10.Ball, "LVCMOS18")

        self.axi_spi.pins["ext_spi_clk"].connect(self.ps.pl_clk[0])
        
        self.axi_interconnect.aximm.connect(self.axi_spi.pins["AXI_LITE"])
        """
        
        
        self.ps.connect_interrupts()
