from .ip import BDIP
from .pin import BDIntfPin

class RFDC(BDIP):
    vlnv = "xilinx.com:ip:usp_rf_data_converter:2.6"

    def __init__(self, parent, name):
        super().__init__(parent, name, [
            ("CONFIG.DAC0_Sampling_Rate", "4.0"),
            ("CONFIG.DAC1_Sampling_Rate", "4.0"),
            ("CONFIG.PRESET", "8x8-ADC-R2C-4GSPS-DAC-C2R")
        ])

        intf_pins = self.cmd(f"get_bd_intf_pins -of {self.obj}").split()

        # CLASS CONFIG.CAN_DEBUG CONFIG.FREQ_HZ LOCATION MODE NAME PATH TYPE VLNV
            
        for pin in intf_pins:
            name = self.cmd(f"get_property NAME [get_bd_intf_pins {pin}]")
            mode = self.cmd(f"get_property MODE [get_bd_intf_pins {pin}]")
            vlnv = self.cmd(f"get_property VLNV [get_bd_intf_pins {pin}]")
            BDIntfPin.construct(vlnv, self, name, mode)
            print(f"RFDC INTF PIN: {name}, {vlnv}, {mode}")
            
        self.ADC_TILES=4
        self.DAC_TILES=2
        
        self.adc_clk = [ self.intf_pins[f"adc{i}_clk"] for i in range(self.ADC_TILES) ]
        self.dac_clk = [ self.intf_pins[f"dac{i}_clk"] for i in range(self.DAC_TILES) ]
        
        self.adc_in = [ self.intf_pins[f"vin{i}_{j}"] for i in range(4) for j in [ "01", "23" ] ]
        self.dac_out = [ self.intf_pins[f"vout{i}{j}"] for i in range(2) for j in range(4) ] 
        
        adc_pins = [ self.intf_pins[f"m{i}{j}_axis"] for i in range(4) for j in range(4) ]
        self.adc_data = list(zip(*([iter(adc_pins)]*2)))
        print(self.adc_data)
        
        self.dac_data = [ self.intf_pins[f"s{i}{j}_axis"] for i in range(2) for j in range(4) ]
        
        self.sysref_in = self.intf_pins["sysref_in"]
            
