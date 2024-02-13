from functools import cached_property

from .ip import BDIP
from .pin import BDIntfPin, all_pins
from .xilinx import BDPSReset, ClockWizard, BDVectorLogic
from .axis import AXISDataWidthConverter, AXISClockConverter
from .piradio import AXISSampleInterleaver


@BDIP.register
class RFDC(BDIP):
    vlnv = "xilinx.com:ip:usp_rf_data_converter:2.6"

    memory_aperture_size = 0x40000

    def __init_IQ(self, parent, name, NCOFreq, sample_freq):
        super().__init__(parent, name, [
            ("CONFIG.ADC0_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC1_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC2_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC3_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.DAC0_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.DAC1_Sampling_Rate", f"{sample_freq/1000000000}"),
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

    def __init_Real(self, parent, name, sample_freq):
        super().__init__(parent, name, [
            ("CONFIG.ADC0_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC1_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC2_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.ADC3_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.DAC0_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.DAC1_Sampling_Rate", f"{sample_freq/1000000000}"),
            ("CONFIG.PRESET", "8x8-ADC-R2C-4GSPS-DAC-C2R"),
            ("CONFIG.ADC_Data_Type00", "0"), 
            ("CONFIG.ADC_Data_Type02", "0"),
            ("CONFIG.ADC_Data_Type10", "0"),
            ("CONFIG.ADC_Data_Type12", "0"), 
            ("CONFIG.ADC_Data_Type20", "0"), 
            ("CONFIG.ADC_Data_Type22", "0"), 
            ("CONFIG.ADC_Data_Type30", "0"), 
            ("CONFIG.ADC_Data_Type32", "0"), 
            ("CONFIG.DAC_Mixer_Type00", "0"), 
            ("CONFIG.DAC_Mixer_Type01", "0"), 
            ("CONFIG.DAC_Mixer_Type02", "0"), 
            ("CONFIG.DAC_Mixer_Type03", "0"), 
            ("CONFIG.DAC_Mixer_Type10", "0"), 
            ("CONFIG.DAC_Mixer_Type11", "0"), 
            ("CONFIG.DAC_Mixer_Type12", "0"), 
            ("CONFIG.DAC_Mixer_Type13", "0"),
            ("CONFIG.DAC_Interpolation_Mode00", "1"),
            ("CONFIG.DAC_Interpolation_Mode01", "1"),
            ("CONFIG.DAC_Interpolation_Mode02", "1"),
            ("CONFIG.DAC_Interpolation_Mode03", "1"),
            ("CONFIG.DAC_Interpolation_Mode10", "1"),
            ("CONFIG.DAC_Interpolation_Mode11", "1"),
            ("CONFIG.DAC_Interpolation_Mode12", "1"),
            ("CONFIG.DAC_Interpolation_Mode13", "1")
        ])
    
    def __init__(self, parent, name, NCOFreq="1.25", real_mode=False, sample_freq=4e9, reclock_adc=False):
        if real_mode == False:
            self.__init_IQ(parent, name, NCOFreq=NCOFreq, sample_freq=sample_freq)
        else:
            self.__init_Real(parent, name, sample_freq=sample_freq)

        self.reclock_adc = reclock_adc
        self.real_mode = real_mode
        self.sample_freq = sample_freq
        
        self.enumerate_pins()
        
        self.ADC_TILES=4
        self.DAC_TILES=2
        
        self.adc_clk = [ self.pins[f"adc{i}_clk"] for i in range(self.ADC_TILES) ]
        self.dac_clk = [ self.pins[f"dac{i}_clk"] for i in range(self.DAC_TILES) ]
        
        self.adc_in = [ self.pins[f"vin{i}_{j}"] for i in range(4) for j in [ "01", "23" ] ]
        self.dac_out = [ self.pins[f"vout{i}{j}"] for i in range(2) for j in range(4) ] 

        if not self.real_mode:
            self.adc_axis = [ self.pins[f"m{i}{j}_axis"] for i in range(4) for j in range(4) ]
        else:
            self.adc_axis = [ self.pins[f"m{i}{j}_axis"] for i in range(4) for j in [0, 2] ]
            
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
        props = {
            "CONFIG.CLKOUT1_REQUESTED_OUT_FREQ": f"{self.sample_freq/8/1e6}",
            "CONFIG.PRIM_IN_FREQ": f"{self.sample_freq/128/1e6}",
            "CONFIG.RESET_BOARD_INTERFACE": "Custom",
            "CONFIG.USE_BOARD_FLOW": "true"
        }
        
        if self.reclock_adc:
            props.update({
                "CONFIG.CLKOUT1_JITTER": "128.356",
                "CONFIG.CLKOUT1_PHASE_ERROR": "174.405",
                "CONFIG.CLKOUT2_JITTER": "140.184",
                "CONFIG.CLKOUT2_PHASE_ERROR": "174.405",
                "CONFIG.CLKOUT2_REQUESTED_OUT_FREQ": f"{self.sample_freq/16/1e6}",
                "CONFIG.CLKOUT2_USED": "true",
                "CONFIG.MMCM_CLKFBOUT_MULT_F": "40.000",
                "CONFIG.MMCM_CLKOUT0_DIVIDE_F": "2.500",
                "CONFIG.MMCM_CLKOUT1_DIVIDE": "5",
                "CONFIG.NUM_OUT_CLKS": "2"
            })

        
        self.adc_axis_clocks = [
            ClockWizard(
                self.parent,
                f"adc{i}_clk_wiz",
                props) for i in range(4) ]

        for i, (rfdc_clk_out, wiz_clk_in) in enumerate(zip(self.adc_axis_ref_clk, all_pins(self.adc_axis_clocks, "clk_in1"))):
            rfdc_clk_out.create_net(f"adc_axis_in_clk{i}").connect(wiz_clk_in)
                    
        self.adc_axis_resetn_nets = [ p.create_net(f"adc_axis_resetn{i}") for i, p in enumerate(all_pins(self.adc_proc_resets, "peripheral_aresetn")) ]

        if self.reclock_adc:
            self.adc_dwidth_conv = [ AXISDataWidthConverter(self.parent,
                                                            f"adc{i}_dwidth_conv",
                                                            {
                                                                "CONFIG.M_TDATA_NUM_BYTES": "32"
                                                            }) for i in range(8) ]

            self.adc_clock_conv = [ AXISClockConverter(self.parent,
                                                           f"adc{i}_clock_conv",
                                                            {
                                                                "CONFIG.IS_ACLK_ASYNC": "0",
                                                                "CONFIG.ACLK_RATIO": "2:1"
                                                            }) for i in range(8) ]
            
            self.adc_full_rate_axis_clk_nets = [ p.create_net(f"adc_axis_full_rate_clk{i}") for i, p in enumerate(all_pins(self.adc_axis_clocks, "clk_out1")) ]
            self.adc_axis_clk_nets = [ p.create_net(f"adc_axis_clk{i}") for i, p in enumerate(all_pins(self.adc_axis_clocks, "clk_out2")) ]

            self.not_resetn = BDVectorLogic(self.parent, "not_resetn", { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": "1" })

            self.not_resetn.pins["Op1"].connect(self.ext_reset_in)

            for c in self.adc_axis_clocks:
                c.pins["reset"].connect(self.not_resetn.pins["Res"])

            
            fr_clk_nets = [ x for x in self.adc_full_rate_axis_clk_nets for _ in range(2) ]
            hr_clk_nets = [ x for x in self.adc_axis_clk_nets for _ in range(2) ]
            rst_nets = [ x for x in self.adc_axis_resetn_nets for _ in range(2) ]
            
            for rst, fr_clk, hr_clk, dc, cc in zip(rst_nets, fr_clk_nets, hr_clk_nets,
                                        self.adc_dwidth_conv, self.adc_clock_conv):
                fr_clk.connect(dc.pins["aclk"], cc.pins["s_axis_aclk"])
                hr_clk.connect(cc.pins["m_axis_aclk"])
                rst.connect(dc.pins["aresetn"])
                rst.connect(cc.pins["m_axis_aresetn"])
                rst.connect(cc.pins["s_axis_aresetn"])
                cc.pins["S_AXIS"].connect(dc.pins["M_AXIS"])
                
            for rfdc_axis, dc in zip(self.adc_axis, self.adc_dwidth_conv):
                rfdc_axis.connect(dc.pins["S_AXIS"])
                
            self.adc_axis = [ cc.pins[f"M_AXIS"] for cc in self.adc_clock_conv ]

            for i, n in enumerate(self.adc_full_rate_axis_clk_nets):
                n.connect(self.pins[f"m{i}_axis_aclk"])            
        else:
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
        
            
        
    def setup_dac_axis(self):
        self.dac_axis_clk_nets = [ p.create_net(f"dac_ref_clk{i}") for i, p in enumerate(self.dac_axis_ref_clk) ]

        for i, n in enumerate(self.dac_axis_clk_nets):
            n.connect(self.pins[f"s{i}_axis_aclk"])

            
        #self.dac_proc_resets = [ BDPSReset(self.parent, f"dac_reset_{i}", None) for i in range(2) ]
        self.dac_axis_resetn_nets = [ p.create_net(f"dac_axis_resetn{i}") for i, p in enumerate(all_pins(self.dac_proc_resets, "peripheral_aresetn")) ]

        for i, n in enumerate(self.dac_axis_resetn_nets):
            n.connect(self.pins[f"s{i}_axis_aresetn"])
        
        for n, p in zip(self.dac_axis_clk_nets, all_pins(self.dac_proc_resets, "slowest_sync_clk")):
            n.connect(p)
        
        self.dac_axis_clk = [ n for n in self.dac_axis_clk_nets for _ in range(4) ]
        self.dac_axis_resetn = [ n for n in self.dac_axis_resetn_nets for _ in range(4) ]

    @cached_property
    def adc_axis_clk(self):
        if self.real_mode:
            return [ n for n in  self.adc_axis_clk_nets for _ in range(2) ]
        else:
            return [ n for n in  self.adc_axis_clk_nets for _ in range(4) ]

    @cached_property
    def adc_axis_resetn(self):
        return [ n for n in self.adc_axis_resetn_nets for _ in range(4) ]

    @cached_property
    def adc_proc_resets(self):
        return [ BDPSReset(self.parent, f"adc_reset_{i}", None) for i in range(4) ]

    @cached_property
    def dac_proc_resets(self):
        return [ BDPSReset(self.parent, f"dac_reset_{i}", None) for i in range(2) ]
        
    
    @cached_property
    def ext_reset_in(self):
        return self.adc_proc_resets[0].pins["ext_reset_in"].create_net("rfdc_ext_reset").connect(*all_pins(self.adc_proc_resets[1:], "ext_reset_in"),
                                                                                                 *all_pins(self.dac_proc_resets, "ext_reset_in"))
        
        
"""        
ALLOWED_SIM_MODELS CLASS COMBINED_SIM_MODEL CONFIG.ADC0_Band CONFIG.ADC0_Clock_Dist CONFIG.ADC0_Clock_Source CONFIG.ADC0_Clock_Source_MX CONFIG.ADC0_Enable CONFIG.ADC0_Fabric_Freq CONFIG.ADC0_Link_Coupling CONFIG.ADC0_Multi_Tile_Sync CONFIG.ADC0_OBS_Fabric_Freq CONFIG.ADC0_Outclk_Freq CONFIG.ADC0_PLL_Enable CONFIG.ADC0_Refclk_Div CONFIG.ADC0_Refclk_Freq CONFIG.ADC0_Sampling_Rate CONFIG.ADC1_Band CONFIG.ADC1_Clock_Dist CONFIG.ADC1_Clock_Source CONFIG.ADC1_Clock_Source_MX CONFIG.ADC1_Enable CONFIG.ADC1_Fabric_Freq CONFIG.ADC1_Link_Coupling CONFIG.ADC1_Multi_Tile_Sync CONFIG.ADC1_OBS_Fabric_Freq CONFIG.ADC1_Outclk_Freq CONFIG.ADC1_PLL_Enable CONFIG.ADC1_Refclk_Div CONFIG.ADC1_Refclk_Freq CONFIG.ADC1_Sampling_Rate CONFIG.ADC2_Band CONFIG.ADC2_Clock_Dist CONFIG.ADC2_Clock_Source CONFIG.ADC2_Clock_Source_MX CONFIG.ADC2_Enable CONFIG.ADC2_Fabric_Freq CONFIG.ADC2_Link_Coupling CONFIG.ADC2_Multi_Tile_Sync CONFIG.ADC2_OBS_Fabric_Freq CONFIG.ADC2_Outclk_Freq CONFIG.ADC2_PLL_Enable CONFIG.ADC2_Refclk_Div CONFIG.ADC2_Refclk_Freq CONFIG.ADC2_Sampling_Rate CONFIG.ADC3_Band CONFIG.ADC3_Clock_Dist CONFIG.ADC3_Clock_Source CONFIG.ADC3_Clock_Source_MX CONFIG.ADC3_Enable CONFIG.ADC3_Fabric_Freq CONFIG.ADC3_Link_Coupling CONFIG.ADC3_Multi_Tile_Sync CONFIG.ADC3_OBS_Fabric_Freq CONFIG.ADC3_Outclk_Freq CONFIG.ADC3_PLL_Enable CONFIG.ADC3_Refclk_Div CONFIG.ADC3_Refclk_Freq CONFIG.ADC3_Sampling_Rate CONFIG.ADC224_En CONFIG.ADC225_En CONFIG.ADC226_En CONFIG.ADC227_En CONFIG.ADC_Bypass_BG_Cal00 CONFIG.ADC_Bypass_BG_Cal01 CONFIG.ADC_Bypass_BG_Cal02 CONFIG.ADC_Bypass_BG_Cal03 CONFIG.ADC_Bypass_BG_Cal10 CONFIG.ADC_Bypass_BG_Cal11 CONFIG.ADC_Bypass_BG_Cal12 CONFIG.ADC_Bypass_BG_Cal13 CONFIG.ADC_Bypass_BG_Cal20 CONFIG.ADC_Bypass_BG_Cal21 CONFIG.ADC_Bypass_BG_Cal22 CONFIG.ADC_Bypass_BG_Cal23 CONFIG.ADC_Bypass_BG_Cal30 CONFIG.ADC_Bypass_BG_Cal31 CONFIG.ADC_Bypass_BG_Cal32 CONFIG.ADC_Bypass_BG_Cal33 CONFIG.ADC_CalOpt_Mode00 CONFIG.ADC_CalOpt_Mode01 CONFIG.ADC_CalOpt_Mode02 CONFIG.ADC_CalOpt_Mode03 CONFIG.ADC_CalOpt_Mode10 CONFIG.ADC_CalOpt_Mode11 CONFIG.ADC_CalOpt_Mode12 CONFIG.ADC_CalOpt_Mode13 CONFIG.ADC_CalOpt_Mode20 CONFIG.ADC_CalOpt_Mode21 CONFIG.ADC_CalOpt_Mode22 CONFIG.ADC_CalOpt_Mode23 CONFIG.ADC_CalOpt_Mode30 CONFIG.ADC_CalOpt_Mode31 CONFIG.ADC_CalOpt_Mode32 CONFIG.ADC_CalOpt_Mode33 CONFIG.ADC_Coarse_Mixer_Freq00 CONFIG.ADC_Coarse_Mixer_Freq01 CONFIG.ADC_Coarse_Mixer_Freq02 CONFIG.ADC_Coarse_Mixer_Freq03 CONFIG.ADC_Coarse_Mixer_Freq10 CONFIG.ADC_Coarse_Mixer_Freq11 CONFIG.ADC_Coarse_Mixer_Freq12 CONFIG.ADC_Coarse_Mixer_Freq13 CONFIG.ADC_Coarse_Mixer_Freq20 CONFIG.ADC_Coarse_Mixer_Freq21 CONFIG.ADC_Coarse_Mixer_Freq22 CONFIG.ADC_Coarse_Mixer_Freq23 CONFIG.ADC_Coarse_Mixer_Freq30 CONFIG.ADC_Coarse_Mixer_Freq31 CONFIG.ADC_Coarse_Mixer_Freq32 CONFIG.ADC_Coarse_Mixer_Freq33 CONFIG.ADC_DSA_RTS CONFIG.ADC_Data_Type00 CONFIG.ADC_Data_Type01 CONFIG.ADC_Data_Type02 CONFIG.ADC_Data_Type03 CONFIG.ADC_Data_Type10 CONFIG.ADC_Data_Type11 CONFIG.ADC_Data_Type12 CONFIG.ADC_Data_Type13 CONFIG.ADC_Data_Type20 CONFIG.ADC_Data_Type21 CONFIG.ADC_Data_Type22 CONFIG.ADC_Data_Type23 CONFIG.ADC_Data_Type30 CONFIG.ADC_Data_Type31 CONFIG.ADC_Data_Type32 CONFIG.ADC_Data_Type33 CONFIG.ADC_Data_Width00 CONFIG.ADC_Data_Width01 CONFIG.ADC_Data_Width02 CONFIG.ADC_Data_Width03 CONFIG.ADC_Data_Width10 CONFIG.ADC_Data_Width11 CONFIG.ADC_Data_Width12 CONFIG.ADC_Data_Width13 CONFIG.ADC_Data_Width20 CONFIG.ADC_Data_Width21 CONFIG.ADC_Data_Width22 CONFIG.ADC_Data_Width23 CONFIG.ADC_Data_Width30 CONFIG.ADC_Data_Width31 CONFIG.ADC_Data_Width32 CONFIG.ADC_Data_Width33 CONFIG.ADC_Debug CONFIG.ADC_Decimation_Mode00 CONFIG.ADC_Decimation_Mode01 CONFIG.ADC_Decimation_Mode02 CONFIG.ADC_Decimation_Mode03 CONFIG.ADC_Decimation_Mode10 CONFIG.ADC_Decimation_Mode11 CONFIG.ADC_Decimation_Mode12 CONFIG.ADC_Decimation_Mode13 CONFIG.ADC_Decimation_Mode20 CONFIG.ADC_Decimation_Mode21 CONFIG.ADC_Decimation_Mode22 CONFIG.ADC_Decimation_Mode23 CONFIG.ADC_Decimation_Mode30 CONFIG.ADC_Decimation_Mode31 CONFIG.ADC_Decimation_Mode32 CONFIG.ADC_Decimation_Mode33 CONFIG.ADC_Dither00 CONFIG.ADC_Dither01 CONFIG.ADC_Dither02 CONFIG.ADC_Dither03 CONFIG.ADC_Dither10 CONFIG.ADC_Dither11 CONFIG.ADC_Dither12 CONFIG.ADC_Dither13 CONFIG.ADC_Dither20 CONFIG.ADC_Dither21 CONFIG.ADC_Dither22 CONFIG.ADC_Dither23 CONFIG.ADC_Dither30 CONFIG.ADC_Dither31 CONFIG.ADC_Dither32 CONFIG.ADC_Dither33 CONFIG.ADC_MTS_Variable_Fabric_Width CONFIG.ADC_Mixer_Mode00 CONFIG.ADC_Mixer_Mode01 CONFIG.ADC_Mixer_Mode02 CONFIG.ADC_Mixer_Mode03 CONFIG.ADC_Mixer_Mode10 CONFIG.ADC_Mixer_Mode11 CONFIG.ADC_Mixer_Mode12 CONFIG.ADC_Mixer_Mode13 CONFIG.ADC_Mixer_Mode20 CONFIG.ADC_Mixer_Mode21 CONFIG.ADC_Mixer_Mode22 CONFIG.ADC_Mixer_Mode23 CONFIG.ADC_Mixer_Mode30 CONFIG.ADC_Mixer_Mode31 CONFIG.ADC_Mixer_Mode32 CONFIG.ADC_Mixer_Mode33 CONFIG.ADC_Mixer_Type00 CONFIG.ADC_Mixer_Type01 CONFIG.ADC_Mixer_Type02 CONFIG.ADC_Mixer_Type03 CONFIG.ADC_Mixer_Type10 CONFIG.ADC_Mixer_Type11 CONFIG.ADC_Mixer_Type12 CONFIG.ADC_Mixer_Type13 CONFIG.ADC_Mixer_Type20 CONFIG.ADC_Mixer_Type21 CONFIG.ADC_Mixer_Type22 CONFIG.ADC_Mixer_Type23 CONFIG.ADC_Mixer_Type30 CONFIG.ADC_Mixer_Type31 CONFIG.ADC_Mixer_Type32 CONFIG.ADC_Mixer_Type33 CONFIG.ADC_NCO_Freq00 CONFIG.ADC_NCO_Freq01 CONFIG.ADC_NCO_Freq02 CONFIG.ADC_NCO_Freq03 CONFIG.ADC_NCO_Freq10 CONFIG.ADC_NCO_Freq11 CONFIG.ADC_NCO_Freq12 CONFIG.ADC_NCO_Freq13 CONFIG.ADC_NCO_Freq20 CONFIG.ADC_NCO_Freq21 CONFIG.ADC_NCO_Freq22 CONFIG.ADC_NCO_Freq23 CONFIG.ADC_NCO_Freq30 CONFIG.ADC_NCO_Freq31 CONFIG.ADC_NCO_Freq32 CONFIG.ADC_NCO_Freq33 CONFIG.ADC_NCO_Phase00 CONFIG.ADC_NCO_Phase01 CONFIG.ADC_NCO_Phase02 CONFIG.ADC_NCO_Phase03 CONFIG.ADC_NCO_Phase10 CONFIG.ADC_NCO_Phase11 CONFIG.ADC_NCO_Phase12 CONFIG.ADC_NCO_Phase13 CONFIG.ADC_NCO_Phase20 CONFIG.ADC_NCO_Phase21 CONFIG.ADC_NCO_Phase22 CONFIG.ADC_NCO_Phase23 CONFIG.ADC_NCO_Phase30 CONFIG.ADC_NCO_Phase31 CONFIG.ADC_NCO_Phase32 CONFIG.ADC_NCO_Phase33 CONFIG.ADC_NCO_RTS CONFIG.ADC_Neg_Quadrature00 CONFIG.ADC_Neg_Quadrature01 CONFIG.ADC_Neg_Quadrature02 CONFIG.ADC_Neg_Quadrature03 CONFIG.ADC_Neg_Quadrature10 CONFIG.ADC_Neg_Quadrature11 CONFIG.ADC_Neg_Quadrature12 CONFIG.ADC_Neg_Quadrature13 CONFIG.ADC_Neg_Quadrature20 CONFIG.ADC_Neg_Quadrature21 CONFIG.ADC_Neg_Quadrature22 CONFIG.ADC_Neg_Quadrature23 CONFIG.ADC_Neg_Quadrature30 CONFIG.ADC_Neg_Quadrature31 CONFIG.ADC_Neg_Quadrature32 CONFIG.ADC_Neg_Quadrature33 CONFIG.ADC_Nyquist00 CONFIG.ADC_Nyquist01 CONFIG.ADC_Nyquist02 CONFIG.ADC_Nyquist03 CONFIG.ADC_Nyquist10 CONFIG.ADC_Nyquist11 CONFIG.ADC_Nyquist12 CONFIG.ADC_Nyquist13 CONFIG.ADC_Nyquist20 CONFIG.ADC_Nyquist21 CONFIG.ADC_Nyquist22 CONFIG.ADC_Nyquist23 CONFIG.ADC_Nyquist30 CONFIG.ADC_Nyquist31 CONFIG.ADC_Nyquist32 CONFIG.ADC_Nyquist33 CONFIG.ADC_OBS00 CONFIG.ADC_OBS01 CONFIG.ADC_OBS02 CONFIG.ADC_OBS03 CONFIG.ADC_OBS10 CONFIG.ADC_OBS11 CONFIG.ADC_OBS12 CONFIG.ADC_OBS13 CONFIG.ADC_OBS20 CONFIG.ADC_OBS21 CONFIG.ADC_OBS22 CONFIG.ADC_OBS23 CONFIG.ADC_OBS30 CONFIG.ADC_OBS31 CONFIG.ADC_OBS32 CONFIG.ADC_OBS33 CONFIG.ADC_OBS_Data_Width00 CONFIG.ADC_OBS_Data_Width01 CONFIG.ADC_OBS_Data_Width02 CONFIG.ADC_OBS_Data_Width03 CONFIG.ADC_OBS_Data_Width10 CONFIG.ADC_OBS_Data_Width11 CONFIG.ADC_OBS_Data_Width12 CONFIG.ADC_OBS_Data_Width13 CONFIG.ADC_OBS_Data_Width20 CONFIG.ADC_OBS_Data_Width21 CONFIG.ADC_OBS_Data_Width22 CONFIG.ADC_OBS_Data_Width23 CONFIG.ADC_OBS_Data_Width30 CONFIG.ADC_OBS_Data_Width31 CONFIG.ADC_OBS_Data_Width32 CONFIG.ADC_OBS_Data_Width33 CONFIG.ADC_OBS_Decimation_Mode00 CONFIG.ADC_OBS_Decimation_Mode01 CONFIG.ADC_OBS_Decimation_Mode02 CONFIG.ADC_OBS_Decimation_Mode03 CONFIG.ADC_OBS_Decimation_Mode10 CONFIG.ADC_OBS_Decimation_Mode11 CONFIG.ADC_OBS_Decimation_Mode12 CONFIG.ADC_OBS_Decimation_Mode13 CONFIG.ADC_OBS_Decimation_Mode20 CONFIG.ADC_OBS_Decimation_Mode21 CONFIG.ADC_OBS_Decimation_Mode22 CONFIG.ADC_OBS_Decimation_Mode23 CONFIG.ADC_OBS_Decimation_Mode30 CONFIG.ADC_OBS_Decimation_Mode31 CONFIG.ADC_OBS_Decimation_Mode32 CONFIG.ADC_OBS_Decimation_Mode33 CONFIG.ADC_RESERVED_1_00 CONFIG.ADC_RESERVED_1_01 CONFIG.ADC_RESERVED_1_02 CONFIG.ADC_RESERVED_1_03 CONFIG.ADC_RESERVED_1_10 CONFIG.ADC_RESERVED_1_11 CONFIG.ADC_RESERVED_1_12 CONFIG.ADC_RESERVED_1_13 CONFIG.ADC_RESERVED_1_20 CONFIG.ADC_RESERVED_1_21...
        """        
