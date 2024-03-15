class DACTile:
    def __init__(self, n, sample_freq, fabric_width):
        self.n = n
        self.sample_freq = sample_freq
        self.fabric_width = fabric_width

    @property
    def fabric_rate(self):
        return self.sample_freq / self.fabric_width

    @property
    def output_clk_rate(self):
        return self.fabric_rate

    def build_props(self):
        return {
            f"CONFIG.DAC{self.n}_Band": 0,
            f"CONFIG.DAC{self.n}_Clock_Dist": 0,
            #f"CONFIG.DAC{self.n}_Clock_Source": 4,
            #f"CONFIG.DAC{self.n}_Clock_Source_MX": 4,
            f"CONFIG.DAC{self.n}_Enable": 1,
            f"CONFIG.DAC{self.n}_Fabric_Freq": "256.000",
            f"CONFIG.DAC{self.n}_Link_Coupling": 0,
            f"CONFIG.DAC{self.n}_Multi_Tile_Sync": "true",
            #f"CONFIG.DAC{self.n}_Outclk_Freq": "256.000",
            f"CONFIG.DAC{self.n}_PLL_Enable": "false",
            f"CONFIG.DAC{self.n}_Refclk_Div": "1",
            f"CONFIG.DAC{self.n}_Refclk_Freq": "4096.000",
            f"CONFIG.DAC{self.n}_Sampling_Rate": "4.096",
            f"CONFIG.DAC{self.n}_VOP": "20.0"
        }

class DAC:
    def __init__(self, tile, block):
        self.tile = tile
        self.block = block
        
    @property
    def fabric_rate(self):
        return self.sample_freq / self.fabric_width
    
    @property
    def output_clk_rate(self):
        return self.fabric_rate

    def build_props(self):
        ns = f"{self.tile.n}{self.block}"
        return {
            f"CONFIG.DAC_Coarse_Mixer_Freq{ns}": 0,
            f"CONFIG.DAC_Data_Type{ns}": 0, # Real
            f"CONFIG.DAC_Data_Width{ns}": f"{self.tile.fabric_width:.3f}",
            f"CONFIG.DAC_Decoder_Mode{ns}": 0,
            f"CONFIG.DAC_Interpolation_Mode{ns}": 1,
            f"CONFIG.DAC_Invsinc_Ctrl{ns}": "false",
            f"CONFIG.DAC_Mixer_Mode{ns}": 2,
            f"CONFIG.DAC_Mixer_Type{ns}": 0,
            f"CONFIG.DAC_Mode{ns}": 0,
            f"CONFIG.DAC_NCO_Freq{ns}": "0.0",
            f"CONFIG.DAC_NCO_Phase{ns}": 0,
            f"CONFIG.DAC_Neg_Quadrature{ns}": "false",
            f"CONFIG.DAC_Nyquist{ns}": 0,
            #CONFIG.DAC_RESERVED_1_{ns}": "false",
            f"CONFIG.DAC_Slice{ns}_Enable": "true",
            f"CONFIG.DAC_TDD_RTS{ns}": 0,
        }
