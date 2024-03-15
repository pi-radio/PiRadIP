class ADCTile:
    def __init__(self, n, sample_freq, fabric_width):
        self.n = n
        self.sample_freq = sample_freq
        self.fabric_width = fabric_width

    @property
    def fabric_rate(self):
        return self.sample_freq / self.fabric_width

    @property
    def output_clk_rate(self):
        return self.fabric_rate / 16
        
    def build_props(self):
        return {
            f"CONFIG.ADC{self.n}_Band": "0",
            f"CONFIG.ADC{self.n}_Clock_Dist": "0",
            #f"CONFIG.ADC{self.n}_Clock_Source": "0",
            #f"CONFIG.ADC{self.n}_Clock_Source_MX": "0",
            f"CONFIG.ADC{self.n}_Enable": "1",
            f"CONFIG.ADC{self.n}_Fabric_Freq": f"{self.fabric_rate:.3f}",
            f"CONFIG.ADC{self.n}_Link_Coupling": "0",
            f"CONFIG.ADC{self.n}_OBS_Fabric_Freq": "0.0",
            #f"CONFIG.ADC{self.n}_Outclk_Freq": "32",
            f"CONFIG.ADC{self.n}_PLL_Enable": "false",
            f"CONFIG.ADC{self.n}_Refclk_Div": "1",
            f"CONFIG.ADC{self.n}_Refclk_Freq": f"{self.sample_freq / 1e6:.3f}",
            f"CONFIG.ADC{self.n}_Sampling_Rate": f"{self.sample_freq / 1e9:.3f}",
        }

class ADC:
    def __init__(self, tile, block):
        self.tile = tile
        self.block = block
        
        

    def build_props(self):
        ns = f"{self.tile.n}{self.block}"

        return {
            f"CONFIG.ADC_Bypass_BG_Cal{ns}": "false",
            f"CONFIG.ADC_CalOpt_Mode{ns}": "1",
            f"CONFIG.ADC_Coarse_Mixer_Freq{ns}": "0",
            f"CONFIG.ADC_Data_Type{ns}": "0",
            f"CONFIG.ADC_Data_Width{ns}": self.tile.fabric_width,
            f"CONFIG.ADC_Decimation_Mode{ns}": "1",
            f"CONFIG.ADC_Dither{ns}": "true",
            f"CONFIG.ADC_Mixer_Mode{ns}": "2", # R2R
            f"CONFIG.ADC_Mixer_Type{ns}": "0", # R2R
            f"CONFIG.ADC_NCO_Freq{ns}": "0.0",
            f"CONFIG.ADC_NCO_Phase{ns}": "0",
            f"CONFIG.ADC_Neg_Quadrature{ns}": "false",
            f"CONFIG.ADC_Nyquist{ns}": "0",
            f"CONFIG.ADC_OBS{ns}": "false",
            f"CONFIG.ADC_OBS_Data_Width{ns}": self.tile.fabric_width,
            f"CONFIG.ADC_OBS_Decimation_Mode{ns}": "1",
            #CONFIG.ADC_RESERVED_1_00              string   false      false
            f"CONFIG.ADC_Slice{ns}_Enable": "true",
            f"CONFIG.ADC_TDD_RTS{ns}": "0",
        }
