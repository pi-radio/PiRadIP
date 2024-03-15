from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

from .clocking import RFDCClocking
from .clock_domain import ADCClockDomain, DACClockDomain

class ADCDomainIndependent(ADCClockDomain):
    @property
    def pin_prefix(self):
        return f"adc{2*self.n}{2*self.n+1}"

    def setup_clock(self):
        props = {
            "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": f"{self.rfdc.adc_fabric_freq}",
            "CONFIG.PRIM_IN_FREQ": f"{self.rfdc.adc_outclk_freq}",
            "CONFIG.RESET_BOARD_INTERFACE": "Custom",
            "CONFIG.USE_BOARD_FLOW": "true"
        }

        self.clk = ClockWizard(
            self.rfdc,
            f"adc{self.n}_clk_wiz",
            props)

        self.rfdc_axis_clk = self.create_net(None, "rfdc_axis_clk")
        self.ext_axis_clk = self.rfdc_axis_clk
        self.reset_clk = self.rfdc_axis_clk
        
        self.rfdc_axis_clk.connect(self.clk.pins["clk_out1"])

        self.rfdc.reset.connect(self.clk.pins["reset"])
        
        
class ADCDomainIndependentReclocked(ADCClockDomain):
    @property
    def pin_prefix(self):
        return f"adc{2*self.n}{2*self.n+1}"

    def setup_clock(self):
        props = {
            "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": f"{self.rfdc.adc_fabric_freq}",
            "CONFIG.PRIM_IN_FREQ": f"{self.rfdc.adc_outclk_freq}",
            "CONFIG.RESET_BOARD_INTERFACE": "Custom",
            "CONFIG.USE_BOARD_FLOW": "true",
            "CONFIG.CLKOUT2_REQUESTED_OUT_FREQ": f"{self.rfdc.adc_fabric_freq/2}",
            "CONFIG.CLKOUT2_USED": "true",
            "CONFIG.OPTIMIZE_CLOCKING_STRUCTURE_EN": "true",
            "CONFIG.NUM_OUT_CLKS": "2"
        }
        
        self.clk = ClockWizard(
            self.rfdc,
            f"adc{self.n}_clk_wiz",
            props)

        self.rfdc_axis_clk = self.create_net(None, "rfdc_axis_clk")
        self.ext_axis_clk = self.create_net(None, "ext_axis_clk")
        self.reset_clk = self.ext_axis_clk
        
        self.rfdc_axis_clk.connect(self.clk.pins["clk_out1"])
        self.ext_axis_clk.connect(self.clk.pins["clk_out2"])

        self.rfdc.reset.connect(self.clk.pins["reset"])

        
class DACDomainIndependent(DACClockDomain):
    @property
    def pin_prefix(self):
        return f"dac{2*self.n}{2*self.n+1}"
    
    def setup_clock(self):
        props = {
            "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": f"{self.rfdc.dac_fabric_freq}",
            "CONFIG.PRIM_IN_FREQ": f"{self.rfdc.dac_outclk_freq}",
            "CONFIG.RESET_BOARD_INTERFACE": "Custom",
            "CONFIG.USE_BOARD_FLOW": "true"
        }

        self.clk = ClockWizard(
            self.rfdc,
            f"dac{self.n}_clk_wiz",
            props)

        self.rfdc_axis_clk = self.create_net(None, "rfdc_axis_clk")
        self.ext_axis_clk = self.rfdc_axis_clk
        self.reset_clk = self.rfdc_axis_clk

        self.rfdc_axis_clk.connect(self.clk.pins["clk_out1"])
        
        self.rfdc.reset.connect(self.clk.pins["reset"])


class RFDCClockingIndependent(RFDCClocking):
    @property
    def adc_resets(self):
        return [ dom.resetn for dom in self.adc_domains for _ in range(self.rfdc.ADC_DCSPT) ]

    @property
    def dac_resets(self):
        return [ dom.resetn for dom in self.dac_domains for _ in range(self.rfdc.DAC_DCSPT) ]

    @property
    def rfdc_adc_axis_clks(self):
        return [ dom.rfdc_axis_clk for dom in self.adc_domains for _ in range(self.rfdc.ADC_DCSPT) ]

    @property
    def ext_adc_axis_clks(self):
        return [ dom.ext_axis_clk for dom in self.adc_domains for _ in range(self.rfdc.ADC_DCSPT) ]
    
    @property
    def rfdc_dac_axis_clks(self):
        return [ dom.rfdc_axis_clk for dom in self.dac_domains for _ in range(self.rfdc.DAC_DCSPT) ]

    @property
    def adc_axis_clk(self):
        return [ dom.ext_axis_clk_pin for dom in self.adc_domains for _ in range(self.rfdc.ADC_DCSPT) ]

    @property
    def dac_axis_clk(self):
        return [ dom.ext_axis_clk_pin for dom in self.dac_domains for _ in range(self.rfdc.DAC_DCSPT) ]

    @property
    def adc_axis_resetn(self):
        return [ dom.ext_axis_rst_pin for dom in self.adc_domains for _ in range(self.rfdc.ADC_DCSPT) ]

    @property
    def dac_axis_resetn(self):
        return [ dom.ext_axis_rst_pin for dom in self.dac_domains for _ in range(self.rfdc.DAC_DCSPT) ]

    def pre_setup(self):
        self.sysref_in = self.make_external(self.rfdc.sysref_in)

        self.not_resetn = BDVectorLogic(self, "not_resetn", { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": "1" })

        self.not_resetn.pins["Op1"].connect(self.resetn)

        self._reset = self.create_net(None, "resetp")
        self.reset.connect(self.not_resetn.pins["Res"])

    @property
    def reset(self):
        return self._reset
        
    def setup_adc(self):
        if self.rfdc.reclock_adc:
            self.adc_domains = [ ADCDomainIndependentReclocked(self.rfdc, ref_clk) for ref_clk in self.rfdc.adc_axis_ref_clk ]
        else:
            self.adc_domains = [ ADCDomainIndependent(self.rfdc, ref_clk) for ref_clk in self.rfdc.adc_axis_ref_clk ]

    def setup_dac(self):
        self.dac_domains = [ DACDomainIndependent(self.rfdc, ref_clk) for ref_clk in self.rfdc.dac_axis_ref_clk ]
            
        
    
    
