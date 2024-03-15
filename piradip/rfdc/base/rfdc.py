from functools import cached_property

import piradip.vivado.bd as bd

print(f"Imported bd: {bd}")

from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

from .adc import ADC, ADCTile
from .dac import DAC, DACTile


@BDIP.register
class RFDC(BDIP):
    vlnv = "xilinx.com:ip:usp_rf_data_converter:2.6"

    memory_aperture_size = 0x40000

    def __init__(self, parent, name, props, sample_freq, mts=False):
        self.ADC_TILES=4
        self.DAC_TILES=2
        self.ADC_DCSPT=2
        self.DAC_DCSPT=4

        self.NADCS = self.ADC_TILES * self.ADC_DCSPT
        self.NDACS = self.DAC_TILES * self.DAC_DCSPT

        self.adc_tiles = [ ADCTile(tile, sample_freq, 8) for tile in range(4) ]
        self.dac_tiles = [ DACTile(tile, sample_freq, 16) for tile in range(2) ]
        
        self.adcs = [ ADC(tile, block) for tile in self.adc_tiles for block in [ 0, 2 ] ]
        self.dacs = [ DAC(tile, block) for tile in self.dac_tiles for block in range(4) ]
                
        bdprops = { 'CONFIG.Preset': 'None' }

        print(f"PROPS: {props}")

        bdprops.update(props)
        
        for tile in self.adc_tiles:
            bdprops.update(tile.build_props())

        for adc in self.adcs:
            bdprops.update(adc.build_props())

        for tile in self.dac_tiles:
            bdprops.update(tile.build_props())

        for dac in self.dacs:
            bdprops.update(dac.build_props())

        
        super().__init__(parent, name, bdprops)

        
        p = self.pins[f"s00_axis"].pins["s00_axis_tdata"]
        
        self._dac_width = p.left - p.right + 1

        p = self.pins[f"m00_axis"].pins["m00_axis_tdata"]

        self._adc_width = p.left - p.right + 1

        print(f"RFDC: Widths: ADC: {self._adc_width} DAC: {self._dac_width}")

        self._adc_fabric_freq = float(self.get_property("CONFIG.ADC0_Fabric_Freq"))
        self._dac_fabric_freq = float(self.get_property("CONFIG.DAC0_Fabric_Freq"))
        
        self._adc_outclk_freq = float(self.get_property("CONFIG.ADC0_Outclk_Freq"))
        self._dac_outclk_freq = float(self.get_property("CONFIG.DAC0_Outclk_Freq"))

        
    @property
    def adc_width(self):
        return self._adc_width

    @property
    def dac_width(self):
        return self._dac_width

    @property
    def adc_fabric_freq(self):
        return self._adc_fabric_freq

    @property
    def dac_fabric_freq(self):
        return self._dac_fabric_freq

    @property
    def adc_outclk_freq(self):
        return self._adc_outclk_freq
    
    @property
    def dac_outclk_freq(self):
        return self._dac_outclk_freq

    @property
    def adc_sample_clocks(self):
        return [ self.pins[f"adc{i}_clk"] for i in range(self.ADC_TILES) ]

    @property
    def dac_sample_clocks(self):
        return [ self.pins[f"dac{i}_clk"] for i in range(self.DAC_TILES) ]

    @property
    def adc_in(self):
        return [ self.pins[f"vin{i}_{j}"] for i in range(4) for j in [ "01", "23" ] ]

    @property
    def dac_out(self):
        return [ self.pins[f"vout{i}{j}"] for i in range(2) for j in range(4) ] 
    
    @property
    def external_pins(self):
        return self.adc_sample_clocks + self.dac_sample_clocks + self.adc_in + self.dac_out

    @property
    def adc_axis_ref_clk(self):
        return [ self.pins[f"clk_adc{i}"] for i in range(self.ADC_TILES) ]

    @property
    def dac_axis_ref_clk(self):
        return [ self.pins[f"clk_dac{i}"] for i in range(self.DAC_TILES) ]

    @property
    def adc_axis(self):
        keys = sorted(filter(lambda x: x[0] == "m" and x[3:] == "_axis", self.pins.keys()))

        print(keys)
                
        return [ self.pins[k] for k in keys ]    

    @property
    def dac_axis(self):
        return [ self.pins[f"s{i}{j}_axis"] for i in range(2) for j in range(4) ]

    @property
    def sysref_in(self):
        return self.pins["sysref_in"]



    def build_props(self):
        props = {
            "CONFIG.PRESET": "None",
        }

        for tile in self.adc_tiles:
            tile.build_props(props)
            
        for adc in self.adcs:
            adc.build_props(props)

                
        # Populate DAC options
        for dac_tile in range(2):
            tile.build_props(props)

        for dac in self.dacs:
            dac.build_props(props)
            
        """    
        for dac_tile in [ 2, 3 ]:
            props[f"CONFIG.DAC{dac_tile}_Enable"] = 0
            for dac_block in range(4):
                ns = f"{dac_tile}{dac_block}"
                props[f"CONFIG.DAC_Slice{ns}_Enable"] = "false"
        """

        return props



        #CONFIG.ADC_DSA_RTS                    string   false      false
        #CONFIG.ADC_Debug                      string   false      false
        #CONFIG.ADC_MTS_Variable_Fabric_Width  string   false      false
        #CONFIG.ADC_NCO_RTS                    string   false      false
        #CONFIG.ADC_RTS                        string   false      false
        #CONFIG.AMS_Factory_Var                string   false      0
        #CONFIG.Analog_Detection               string   false      1
        #CONFIG.Auto_Calibration_Freeze        string   false      false
        #CONFIG.Axiclk_Freq                    string   false      100.0
        #CONFIG.Calibration_Freeze             string   false      false
        #CONFIG.Calibration_Time               string   false      10
        #CONFIG.Clock_Forwarding               string   false      false
        #CONFIG.Component_Name                 string   false      BetelgeuseTest2_usp_rf_data_converter_0_0
        #CONFIG.Converter_Setup                string   false      1
        #CONFIG.PL_Clock_Freq                  string   false      100.0
        #CONFIG.PRESET                         string   false      None
        #CONFIG.RESERVED_3                     string   false      110000
        #CONFIG.RF_Analyzer                    string   false      0
        #CONFIG.Sysref_Source                  string   false      1
        #CONFIG.VNC_Include_Fs2_Change         string   false      true
        #CONFIG.VNC_Include_OIS_Change         string   false      true
        #CONFIG.VNC_Testing                    string   false      false
        #CONFIG.disable_bg_cal_en              string   false      1        
        #CONFIG.DAC_Debug                      string   false      false
        #CONFIG.DAC_MTS_Variable_Fabric_Width  string   false      false
        #CONFIG.DAC_NCO_RTS                    string   false      false
        #CONFIG.DAC_Output_Current             string   false      0
        #CONFIG.DAC_RTS                        string   false      false
        #CONFIG.DAC_VOP_Mode                   string   false      1
        #CONFIG.DAC_VOP_RTS                    string   false      false
        
