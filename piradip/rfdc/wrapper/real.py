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

class RFDCReal(RFDCWrapper):
    def __init__(self, parent, name, sample_freq, reclock_adc, clocking=RFDCClockingIndependent):
        super().__init__(parent, name, sample_freq, reclock_adc, clocking=clocking)
                
    def setup_adc_axis(self):
        if self.reclock_adc:
            self.reclockers = [ AXISReclocker(self, n) for n in range(self.NADCS) ]

            for rc, adc in zip(self.reclockers, self.adc_axis):
                self.connect(rc.adc_in, adc)
                    
            return [ self.reexport(r.adc_out, name=n)
                     for r, n in zip(self.reclockers, self.adc_port_names) ]

        return super().setup_adc_axis()
