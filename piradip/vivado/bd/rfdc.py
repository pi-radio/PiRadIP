from functools import cached_property

from .ip import BDIP
from .pin import BDIntfPin, all_pins
from .xilinx import BDPSReset, ClockWizard
from .piradio import AXISSampleInterleaver

@BDIP.register
class RFDC(BDIP):
    vlnv = "xilinx.com:ip:usp_rf_data_converter:2.6"

    memory_aperture_size = 0x40000
    
    def __init__(self, parent, name, NCOFreq="1.25"):
        super().__init__(parent, name, [
            ("CONFIG.DAC0_Sampling_Rate", "4.0"),
            ("CONFIG.DAC1_Sampling_Rate", "4.0"),
            ("CONFIG.PRESET", "8x8-ADC-R2C-4GSPS-DAC-C2R"),
            ("CONFIG.ADC_NCO_Freq00", NCOFreq),
            ("CONFIG.ADC_NCO_Freq02", NCOFreq),
            ("CONFIG.ADC_NCO_Freq10", NCOFreq),
            ("CONFIG.ADC_NCO_Freq12", NCOFreq),
            ("CONFIG.ADC_NCO_Freq20", NCOFreq),
            ("CONFIG.ADC_NCO_Freq22", NCOFreq),
            ("CONFIG.ADC_NCO_Freq30", NCOFreq),
            ("CONFIG.ADC_NCO_Freq32", NCOFreq),
            ("CONFIG.DAC_NCO_Freq00", NCOFreq),
            ("CONFIG.DAC_NCO_Freq01", NCOFreq),
            ("CONFIG.DAC_NCO_Freq02", NCOFreq),
            ("CONFIG.DAC_NCO_Freq03", NCOFreq),
            ("CONFIG.DAC_NCO_Freq10", NCOFreq),
            ("CONFIG.DAC_NCO_Freq11", NCOFreq),
            ("CONFIG.DAC_NCO_Freq12", NCOFreq),
            ("CONFIG.DAC_NCO_Freq13", NCOFreq),
        ])

        self.enumerate_pins()
        
        self.ADC_TILES=4
        self.DAC_TILES=2
        
        self.adc_clk = [ self.pins[f"adc{i}_clk"] for i in range(self.ADC_TILES) ]
        self.dac_clk = [ self.pins[f"dac{i}_clk"] for i in range(self.DAC_TILES) ]
        
        self.adc_in = [ self.pins[f"vin{i}_{j}"] for i in range(4) for j in [ "01", "23" ] ]
        self.dac_out = [ self.pins[f"vout{i}{j}"] for i in range(2) for j in range(4) ] 
        
        self.adc_axis = [ self.pins[f"m{i}{j}_axis"] for i in range(4) for j in range(4) ]
        
        self.dac_axis = [ self.pins[f"s{i}{j}_axis"] for i in range(2) for j in range(4) ]

        self.adc_axis_ref_clk = [ self.pins[f"clk_adc{i}"] for i in range(4) ]
        self.dac_axis_ref_clk = [ self.pins[f"clk_dac{i}"] for i in range(2) ]
        
        self.sysref_in = self.pins["sysref_in"]

    def setup_interleave(self):
        self.interleavers = [
            AXISSampleInterleaver(self.parent,
                                  f"adc_interleaver{i}",
                                  {
                                      "CONFIG.IQ_OUT_WIDTH": 256,
                                      "CONFIG.I_IN_WIDTH": 128,
                                      "CONFIG.Q_IN_WIDTH": 128
                                  } ) for i in range(8) ]

        self.adc_axis_clk = [ n for n in self.adc_axis_clk_nets for _ in range(2) ]
        self.adc_axis_resetn = [ n for n in  self.adc_axis_resetn_nets for _ in range(2) ]
        
        for il, clk, rst in zip(self.interleavers, self.adc_axis_clk, self.adc_axis_resetn):
            clk.connect(il.pins["I_in_clk"], il.pins["Q_in_clk"], il.pins["IQ_out_clk"])
            rst.connect(il.pins["I_in_resetn"], il.pins["Q_in_resetn"], il.pins["IQ_out_resetn"])
        
        for il, (I, Q) in zip(self.interleavers, list(zip(*([iter(self.adc_axis)]*2)))):
            il.pins["I_IN"].connect(I)
            il.pins["Q_IN"].connect(Q)

        self.adc_axis = [ p.create_net(f"adc_iq{i}") for i, p in enumerate(all_pins(self.interleavers, "IQ_OUT")) ]

        self.i_en = [ p.create_net(f"i_en{i}") for i, p in enumerate(all_pins(self.interleavers, "i_en")) ]
        self.q_en = [ p.create_net(f"q_en{i}") for i, p in enumerate(all_pins(self.interleavers, "q_en")) ]
        
        
    def setup_adc_axis(self):
        self.adc_axis_clocks = [
            ClockWizard(
                self.parent,
                f"adc{i}_clk_wiz",
                {
                    "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": "500.000",
                    "CONFIG.PRIM_IN_FREQ": "31.250",
                    "CONFIG.RESET_BOARD_INTERFACE": "Custom",
                    "CONFIG.USE_BOARD_FLOW": "true"
                } ) for i in range(4) ]

        for i, (rfdc_clk_out, wiz_clk_in) in enumerate(zip(self.adc_axis_ref_clk, all_pins(self.adc_axis_clocks, "clk_in1"))):
            rfdc_clk_out.create_net(f"adc_axis_in_clk{i}").connect(wiz_clk_in)
                    
        self.adc_proc_resets = [ BDPSReset(self.parent, f"adc_reset_{i}", None) for i in range(4) ]
        self.adc_axis_resetn_nets = [ p.create_net(f"adc_axis_resetn{i}") for i, p in enumerate(all_pins(self.adc_proc_resets, "peripheral_aresetn")) ]

        self.adc_axis_clk_nets = [ p.create_net(f"adc_axis_clk{i}") for i, p in enumerate(all_pins(self.adc_axis_clocks, "clk_out1")) ]

        for i, n in enumerate(self.adc_axis_clk_nets):
            n.connect(self.pins[f"m{i}_axis_aclk"])

        for i, n in enumerate(self.adc_axis_resetn_nets):
            n.connect(self.pins[f"m{i}_axis_aresetn"])
            
        # Connect the DCM lock
        for n, (op, ip) in enumerate(zip(all_pins(self.adc_axis_clocks, "locked"), all_pins(self.adc_proc_resets, "dcm_locked"))):
            op.create_net(f"adc_clk_locked{n}").connect(ip)
        
        for n, p in zip(self.adc_axis_clk_nets, all_pins(self.adc_proc_resets, "slowest_sync_clk")):
            n.connect(p)
        
        self.adc_axis_clk = [ n for n in  self.adc_axis_clk_nets for _ in range(4) ]
        self.adc_axis_resetn = [ n for n in self.adc_axis_resetn_nets for _ in range(4) ]
        
    def setup_dac_axis(self):
        self.dac_axis_clk_nets = [ p.create_net(f"dac_ref_clk{i}") for i, p in enumerate(self.dac_axis_ref_clk) ]

        for i, n in enumerate(self.dac_axis_clk_nets):
            n.connect(self.pins[f"s{i}_axis_aclk"])

            
        self.dac_proc_resets = [ BDPSReset(self.parent, f"dac_reset_{i}", None) for i in range(2) ]
        self.dac_axis_resetn_nets = [ p.create_net(f"dac_axis_resetn{i}") for i, p in enumerate(all_pins(self.dac_proc_resets, "peripheral_aresetn")) ]

        for i, n in enumerate(self.dac_axis_resetn_nets):
            n.connect(self.pins[f"s{i}_axis_aresetn"])
        
        for n, p in zip(self.dac_axis_clk_nets, all_pins(self.dac_proc_resets, "slowest_sync_clk")):
            n.connect(p)
        
        self.dac_axis_clk = [ n for n in self.dac_axis_clk_nets for _ in range(4) ]
        self.dac_axis_resetn = [ n for n in self.dac_axis_resetn_nets for _ in range(4) ]

    @cached_property
    def ext_reset_in(self):
        return self.adc_proc_resets[0].pins["ext_reset_in"].create_net("rfdc_ext_reset").connect(*all_pins(self.adc_proc_resets[1:], "ext_reset_in"),
                                                                                                 *all_pins(self.dac_proc_resets, "ext_reset_in"))
        
        
