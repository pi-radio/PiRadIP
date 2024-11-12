from functools import cached_property

from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

from piradip.rfdc.base import RFDC
from piradip.rfdc.clocking import *

class passthru_attr:
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, objtype=None):
        print(f"Passing along {self.f.__name__} {getattr(obj.rfdc, self.f.__name__)}")
        return getattr(obj.rfdc, self.f.__name__)
        
class RFDCWrapper(BDHier):
    def __init__(self, parent, name, sample_freq, reclock_adc, adc_mode="Real", dac_mode="Real", NCO_freq=1.0, clocking=RFDCClockingIndependent):
        super().__init__(parent, name)
        
        self.sample_freq = sample_freq
        self.reclock_adc = reclock_adc

        self.clocking = clocking(self)

        props = {}

        self.clocking.update_rfdc_props(props)

        self.update_rfdc_props(props)
                
        self.rfdc = RFDC(self, "rf_data_converter",
                         props,
                         sample_freq=sample_freq,
                         adc_mode=adc_mode,
                         dac_mode=dac_mode,
                         NCO_freq=NCO_freq)

        self.adc_prefixes = [ f"adc{i}_axis" for i in range(self.NADCS) ]
        self.dac_prefixes = [ f"dac{i}_axis" for i in range(self.NDACS) ]
        
        self.adc_port_names = self.adc_prefixes
        self.adc_clk_names = [ f"{s}_aclk" for s in self.adc_prefixes ]
        self.adc_rst_names = [ f"{s}_aresetn" for s in self.adc_prefixes ]

        self.dac_port_names = self.dac_prefixes
        self.dac_clk_names = [ f"{s}_aclk" for s in self.dac_prefixes ]
        self.dac_rst_names = [ f"{s}_aresetn" for s in self.dac_prefixes ]

        print(f"Port names: {self.adc_port_names}")
        
        #
        # Export needed pins
        #        
        self._resetn = create_pin(self, "resetn")
        self._resetn.create()
                
        self.clocking.setup_clocking()

        for adc_dom in self.clocking.adc_domains:
            adc_dom.rfdc_axis_clk.connect(self.rfdc.pins[f"m{adc_dom.n}_axis_aclk"])
            adc_dom.resetn.connect(self.rfdc.pins[f"m{adc_dom.n}_axis_aresetn"])

        for dac_dom in self.clocking.dac_domains:
            dac_dom.rfdc_axis_clk.connect(self.rfdc.pins[f"s{dac_dom.n}_axis_aclk"])
            dac_dom.resetn.connect(self.rfdc.pins[f"s{dac_dom.n}_axis_aresetn"])

        
        self._adc_axis = self.setup_adc_axis()
        self._dac_axis = self.setup_dac_axis()
            
        self.reexport(self.rfdc.pins["s_axi"], name="S_AXI")
        self.reexport(self.rfdc.pins["s_axi_aclk"])
        self.reexport(self.rfdc.pins["s_axi_aresetn"])

        # Figure out how to contain these within the hierarchical block and constrain them automagically
        
        for p in self.adc_sample_clocks + self.dac_sample_clocks:
            np = self.make_external(p)
            p.set_property_list([("CONFIG.FREQ_HZ", "4096000000.0")])

        for p in self.rfdc.adc_in + self.rfdc.dac_out:
            np = self.make_external(p)
        
        self.irq = self.reexport(self.rfdc.pins["irq"])


            
    def setup_adc_axis(self):
        print("Setting up ADC streams...")
        return [ self.reexport(x, name=n) for x, n in zip(self.rfdc.adc_axis, self.adc_port_names) ]

    def setup_dac_axis(self):
        print("Setting up DAC streams...")
        return [ self.reexport(x, name=n) for x, n in zip(self.rfdc.dac_axis, self.dac_port_names) ]

    def update_rfdc_props(self, props):
        pass
    
    @property
    def resetn(self):
        return self._resetn

    def __getattr__(self, n):
        if hasattr(self.rfdc, n):
            return getattr(self.rfdc, n)
        
        raise AttributeError(n)

    @property
    def adc_axis_clk(self):
        return self.clocking.adc_axis_clk

    @property
    def dac_axis_clk(self):
        return self.clocking.dac_axis_clk
    
    @property
    def adc_axis_resetn(self):
        try:
            return self.clocking.adc_axis_resetn
        except Exception as e:
            print(f"Error fetching adc resets: {e}")
            exit()
            
    @property
    def dac_axis_resetn(self):
        return self.clocking.dac_axis_resetn

    @property
    def adc_axis(self):
        return self._adc_axis

    @property
    def dac_axis(self):
        return self._dac_axis

            

    @property
    def adc_data_width(self):
        return 8

    @property
    def dac_data_width(self):
        return 16


"""
CONFIG.mADC_Band                      string   false      0
CONFIG.mADC_Bypass_BG_Cal00           string   false      false
CONFIG.mADC_Bypass_BG_Cal01           string   false      false
CONFIG.mADC_Bypass_BG_Cal02           string   false      false
CONFIG.mADC_Bypass_BG_Cal03           string   false      false
CONFIG.mADC_CalOpt_Mode00             string   false      1
CONFIG.mADC_CalOpt_Mode01             string   false      1
CONFIG.mADC_CalOpt_Mode02             string   false      1
CONFIG.mADC_CalOpt_Mode03             string   false      1
CONFIG.mADC_Coarse_Mixer_Freq00       string   false      0
CONFIG.mADC_Coarse_Mixer_Freq01       string   false      0
CONFIG.mADC_Coarse_Mixer_Freq02       string   false      0
CONFIG.mADC_Coarse_Mixer_Freq03       string   false      0
CONFIG.mADC_Data_Type00               string   false      0
CONFIG.mADC_Data_Type01               string   false      0
CONFIG.mADC_Data_Type02               string   false      0
CONFIG.mADC_Data_Type03               string   false      0
CONFIG.mADC_Data_Width00              string   false      8
CONFIG.mADC_Data_Width01              string   false      8
CONFIG.mADC_Data_Width02              string   false      8
CONFIG.mADC_Data_Width03              string   false      8
CONFIG.mADC_Decimation_Mode00         string   false      0
CONFIG.mADC_Decimation_Mode01         string   false      0
CONFIG.mADC_Decimation_Mode02         string   false      0
CONFIG.mADC_Decimation_Mode03         string   false      0
CONFIG.mADC_Dither00                  string   false      true
CONFIG.mADC_Dither01                  string   false      true
CONFIG.mADC_Dither02                  string   false      true
CONFIG.mADC_Dither03                  string   false      true
CONFIG.mADC_Enable                    string   false      0
CONFIG.mADC_Fabric_Freq               string   false      0.0
CONFIG.mADC_Link_Coupling             string   false      0
CONFIG.mADC_Mixer_Mode00              string   false      2
CONFIG.mADC_Mixer_Mode01              string   false      2
CONFIG.mADC_Mixer_Mode02              string   false      2
CONFIG.mADC_Mixer_Mode03              string   false      2
CONFIG.mADC_Mixer_Type00              string   false      3
CONFIG.mADC_Mixer_Type01              string   false      3
CONFIG.mADC_Mixer_Type02              string   false      3
CONFIG.mADC_Mixer_Type03              string   false      3
CONFIG.mADC_Multi_Tile_Sync           string   false      false
CONFIG.mADC_NCO_Freq00                string   false      0.0
CONFIG.mADC_NCO_Freq01                string   false      0.0
CONFIG.mADC_NCO_Freq02                string   false      0.0
CONFIG.mADC_NCO_Freq03                string   false      0.0
CONFIG.mADC_NCO_Phase00               string   false      0
CONFIG.mADC_NCO_Phase01               string   false      0
CONFIG.mADC_NCO_Phase02               string   false      0
CONFIG.mADC_NCO_Phase03               string   false      0
CONFIG.mADC_Neg_Quadrature00          string   false      false
CONFIG.mADC_Neg_Quadrature01          string   false      false
CONFIG.mADC_Neg_Quadrature02          string   false      false
CONFIG.mADC_Neg_Quadrature03          string   false      false
CONFIG.mADC_Nyquist00                 string   false      0
CONFIG.mADC_Nyquist01                 string   false      0
CONFIG.mADC_Nyquist02                 string   false      0
CONFIG.mADC_Nyquist03                 string   false      0
CONFIG.mADC_OBS00                     string   false      false
CONFIG.mADC_OBS01                     string   false      false
CONFIG.mADC_OBS02                     string   false      false
CONFIG.mADC_OBS03                     string   false      false
CONFIG.mADC_Outclk_Freq               string   false      15.625
CONFIG.mADC_PLL_Enable                string   false      false
CONFIG.mADC_RESERVED_1_00             string   false      false
CONFIG.mADC_RESERVED_1_01             string   false      false
CONFIG.mADC_RESERVED_1_02             string   false      false
CONFIG.mADC_RESERVED_1_03             string   false      false
CONFIG.mADC_Refclk_Div                string   false      1
CONFIG.mADC_Refclk_Freq               string   false      2000.000
CONFIG.mADC_Sampling_Rate             string   false      2.0
CONFIG.mADC_Slice00_Enable            string   false      false
CONFIG.mADC_Slice01_Enable            string   false      false
CONFIG.mADC_Slice02_Enable            string   false      false
CONFIG.mADC_Slice03_Enable            string   false      false
CONFIG.mADC_TDD_RTS00                 string   false      0
CONFIG.mADC_TDD_RTS01                 string   false      0
CONFIG.mADC_TDD_RTS02                 string   false      0
CONFIG.mADC_TDD_RTS03                 string   false      0
CONFIG.mDAC_Band                      string   false      0
CONFIG.mDAC_Coarse_Mixer_Freq00       string   false      0
CONFIG.mDAC_Coarse_Mixer_Freq01       string   false      0
CONFIG.mDAC_Coarse_Mixer_Freq02       string   false      0
CONFIG.mDAC_Coarse_Mixer_Freq03       string   false      0
CONFIG.mDAC_Data_Type00               string   false      0
CONFIG.mDAC_Data_Type01               string   false      0
CONFIG.mDAC_Data_Type02               string   false      0
CONFIG.mDAC_Data_Type03               string   false      0
CONFIG.mDAC_Data_Width00              string   false      16
CONFIG.mDAC_Data_Width01              string   false      16
CONFIG.mDAC_Data_Width02              string   false      16
CONFIG.mDAC_Data_Width03              string   false      16
CONFIG.mDAC_Decoder_Mode00            string   false      0
CONFIG.mDAC_Decoder_Mode01            string   false      0
CONFIG.mDAC_Decoder_Mode02            string   false      0
CONFIG.mDAC_Decoder_Mode03            string   false      0
CONFIG.mDAC_Enable                    string   false      0
CONFIG.mDAC_Fabric_Freq               string   false      0.0
CONFIG.mDAC_Interpolation_Mode00      string   false      0
CONFIG.mDAC_Interpolation_Mode01      string   false      0
CONFIG.mDAC_Interpolation_Mode02      string   false      0
CONFIG.mDAC_Interpolation_Mode03      string   false      0
CONFIG.mDAC_Invsinc_Ctrl00            string   false      false
CONFIG.mDAC_Invsinc_Ctrl01            string   false      false
CONFIG.mDAC_Invsinc_Ctrl02            string   false      false
CONFIG.mDAC_Invsinc_Ctrl03            string   false      false
CONFIG.mDAC_Link_Coupling             string   false      0
CONFIG.mDAC_Mixer_Mode00              string   false      2
CONFIG.mDAC_Mixer_Mode01              string   false      2
CONFIG.mDAC_Mixer_Mode02              string   false      2
CONFIG.mDAC_Mixer_Mode03              string   false      2
CONFIG.mDAC_Mixer_Type00              string   false      3
CONFIG.mDAC_Mixer_Type01              string   false      3
CONFIG.mDAC_Mixer_Type02              string   false      3
CONFIG.mDAC_Mixer_Type03              string   false      3
CONFIG.mDAC_Mode00                    string   false      0
CONFIG.mDAC_Mode01                    string   false      0
CONFIG.mDAC_Mode02                    string   false      0
CONFIG.mDAC_Mode03                    string   false      0
CONFIG.mDAC_Multi_Tile_Sync           string   false      false
CONFIG.mDAC_NCO_Freq00                string   false      0.0
CONFIG.mDAC_NCO_Freq01                string   false      0.0
CONFIG.mDAC_NCO_Freq02                string   false      0.0
CONFIG.mDAC_NCO_Freq03                string   false      0.0
CONFIG.mDAC_NCO_Phase00               string   false      0
CONFIG.mDAC_NCO_Phase01               string   false      0
CONFIG.mDAC_NCO_Phase02               string   false      0
CONFIG.mDAC_NCO_Phase03               string   false      0
CONFIG.mDAC_Neg_Quadrature00          string   false      false
CONFIG.mDAC_Neg_Quadrature01          string   false      false
CONFIG.mDAC_Neg_Quadrature02          string   false      false
CONFIG.mDAC_Neg_Quadrature03          string   false      false
CONFIG.mDAC_Nyquist00                 string   false      0
CONFIG.mDAC_Nyquist01                 string   false      0
CONFIG.mDAC_Nyquist02                 string   false      0
CONFIG.mDAC_Nyquist03                 string   false      0
CONFIG.mDAC_Outclk_Freq               string   false      50.000
CONFIG.mDAC_PLL_Enable                string   false      false
CONFIG.mDAC_RESERVED_1_00             string   false      false
CONFIG.mDAC_RESERVED_1_01             string   false      false
CONFIG.mDAC_RESERVED_1_02             string   false      false
CONFIG.mDAC_RESERVED_1_03             string   false      false
CONFIG.mDAC_Refclk_Div                string   false      1
CONFIG.mDAC_Refclk_Freq               string   false      6400.000
CONFIG.mDAC_Sampling_Rate             string   false      6.4
CONFIG.mDAC_Slice00_Enable            string   false      false
CONFIG.mDAC_Slice01_Enable            string   false      false
CONFIG.mDAC_Slice02_Enable            string   false      false
CONFIG.mDAC_Slice03_Enable            string   false      false
CONFIG.mDAC_TDD_RTS00                 string   false      0
CONFIG.mDAC_TDD_RTS01                 string   false      0
CONFIG.mDAC_TDD_RTS02                 string   false      0
CONFIG.mDAC_TDD_RTS03                 string   false      0
CONFIG.mDAC_VOP                       string   false      20.0
CONFIG.production_simulation          string   false      0
CONFIG.tb_adc_fft                     string   false      true
CONFIG.tb_dac_fft                     string   false      true
CONFIG.use_bram                       string   false      1
"""
