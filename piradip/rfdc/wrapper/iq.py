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

class RFDCIQ(RFDCWrapper):
    def __init__(self, parent, name, sample_freq, reclock_adc, clocking=RFDCClockingIndependent):
        super().__init__(parent, name, sample_freq, reclock_adc, adc_mode="IQ", dac_mode="IQ", NCO_freq=1.0, clocking=clocking)

    def update_rfdc_props(self, props):
        props["CONFIG.ADC_Decimation_Mode00"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode02"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode10"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode12"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode20"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode22"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode30"] = "{2}"
        props["CONFIG.ADC_Decimation_Mode32"] = "{2}"
        
    def setup_adc_axis(self):
        print(f"Creating interleavers")
        self.interleavers = [ AXISSampleInterleaver(self,
                                                    f"adc{i}_interleave",
                                                    {
                                                        "CONFIG.IQ_OUT_WIDTH": 256,
                                                        "CONFIG.I_IN_WIDTH": 128,
                                                        "CONFIG.Q_IN_WIDTH": 128
                                                    } ) for i in range(8) ]

        adc_ports = [ (f"m{i}{j}_axis", f"m{i}{j+1}_axis") for i in range(4) for j in [0, 2] ]

        for n, il in enumerate(self.interleavers):
            self.reexport(il.pins["i_en"], name=f"i{n}_en")
            self.reexport(il.pins["q_en"], name=f"q{n}_en")
        
        for il, (iport, qport) in zip(self.interleavers, adc_ports):
            self.rfdc.pins[iport].connect(il.pins["I_IN"])
            self.rfdc.pins[qport].connect(il.pins["Q_IN"])

            clk = iport[:2] + "_axis_aclk"
            rst = iport[:2] + "_axis_aresetn"

            self.rfdc.pins[clk].connect(il.pins["I_in_clk"])
            self.rfdc.pins[clk].connect(il.pins["Q_in_clk"])
            self.rfdc.pins[clk].connect(il.pins["IQ_out_clk"])
            
            self.rfdc.pins[rst].connect(il.pins["I_in_resetn"])
            self.rfdc.pins[rst].connect(il.pins["Q_in_resetn"])
            self.rfdc.pins[rst].connect(il.pins["IQ_out_resetn"])

        if self.reclock_adc:
            self.reclockers = [ AXISReclocker(self, n) for n in range(self.NADCS) ]

            for rc, adc in zip(self.reclockers, self.interleavers):
                self.connect(rc.adc_in, adc.pins["IQ_OUT"])
                    
            return [ self.reexport(r.adc_out, name=n)
                     for r, n in zip(self.reclockers, self.adc_port_names) ]
        
        return [ self.reexport(x.pins["IQ_OUT"], name=n) for x, n in zip(self.interleavers, self.adc_port_names) ]        

        
