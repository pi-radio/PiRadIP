from functools import cached_property

from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

from piradip.rfdc.base import RFDC
from piradip.rfdc.clocking import *

from .wrapper import *
from .reclocker import *

class AXISReclocker:
    def __init__(self, rfdc, n):
        self.rfdc = rfdc
        self.n = n
        
        self.adc_dwidth_conv = AXISDataWidthConverter(self.rfdc,
                                   f"adc{self.n}_dwidth_conv",
                                   {
                                       "CONFIG.M_TDATA_NUM_BYTES": "32"
                                   })

        self.adc_clock_conv = AXISClockConverter(self.rfdc,
                               f"adc{self.n}_clock_conv",
                               {
                                   "CONFIG.IS_ACLK_ASYNC": "0",
                                   "CONFIG.ACLK_RATIO": "2:1"
                               })

        self.adc_dwidth_conv.pins["aclk"].connect(self.rfdc.clocking.rfdc_adc_axis_clks[self.n])
        self.adc_dwidth_conv.pins["aresetn"].connect(self.rfdc.clocking.adc_resets[self.n])

        self.adc_clock_conv.pins["s_axis_aclk"].connect(self.rfdc.clocking.rfdc_adc_axis_clks[self.n])
        self.adc_clock_conv.pins["m_axis_aclk"].connect(self.rfdc.clocking.ext_adc_axis_clks[self.n])
        self.adc_clock_conv.pins["s_axis_aresetn"].connect(self.rfdc.clocking.adc_resets[self.n])
        self.adc_clock_conv.pins["m_axis_aresetn"].connect(self.rfdc.clocking.adc_resets[self.n])

        self.adc_dwidth_conv.pins["M_AXIS"].connect(self.adc_clock_conv.pins["S_AXIS"])

    @property
    def adc_in(self):
        return self.adc_dwidth_conv.pins["S_AXIS"]

    @property
    def adc_out(self):
        return self.adc_clock_conv.pins["M_AXIS"]
