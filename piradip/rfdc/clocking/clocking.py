from functools import cached_property

from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

from .clock_domain import *

class RFDCClocking:
    def __init__(self, rfdc):
        self.rfdc = rfdc
        self.adc_domains = []
        self.dac_domains = []

    def update_rfdc_props(self, props):
        pass
        
    def setup_clocking(self):
        self.pre_setup()
        
        self.setup_adc()
        self.setup_dac()

    def pre_setup(self):
        pass

    def setup_adc(self):
        pass

    def setup_dac(self):
        pass

    
