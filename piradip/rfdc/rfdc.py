from .rfdc_base import RFDC
from .rfdc_clocking import *
from .rfdc_wrapper import *


    
        
"""        
ALLOWED_SIM_MODELS CLASS COMBINED_SIM_MODEL CONFIG.ADC0_Band CONFIG.ADC0_Clock_Dist CONFIG.ADC0_Clock_Source CONFIG.ADC0_Clock_Source_MX CONFIG.ADC0_Enable CONFIG.ADC0_Fabric_Freq CONFIG.ADC0_Link_Coupling CONFIG.ADC0_Multi_Tile_Sync CONFIG.ADC0_OBS_Fabric_Freq CONFIG.ADC0_Outclk_Freq CONFIG.ADC0_PLL_Enable CONFIG.ADC0_Refclk_Div CONFIG.ADC0_Refclk_Freq CONFIG.ADC0_Sampling_Rate CONFIG.ADC1_Band CONFIG.ADC1_Clock_Dist CONFIG.ADC1_Clock_Source CONFIG.ADC1_Clock_Source_MX CONFIG.ADC1_Enable CONFIG.ADC1_Fabric_Freq CONFIG.ADC1_Link_Coupling CONFIG.ADC1_Multi_Tile_Sync CONFIG.ADC1_OBS_Fabric_Freq CONFIG.ADC1_Outclk_Freq CONFIG.ADC1_PLL_Enable CONFIG.ADC1_Refclk_Div CONFIG.ADC1_Refclk_Freq CONFIG.ADC1_Sampling_Rate CONFIG.ADC2_Band CONFIG.ADC2_Clock_Dist CONFIG.ADC2_Clock_Source CONFIG.ADC2_Clock_Source_MX CONFIG.ADC2_Enable CONFIG.ADC2_Fabric_Freq CONFIG.ADC2_Link_Coupling CONFIG.ADC2_Multi_Tile_Sync CONFIG.ADC2_OBS_Fabric_Freq CONFIG.ADC2_Outclk_Freq CONFIG.ADC2_PLL_Enable CONFIG.ADC2_Refclk_Div CONFIG.ADC2_Refclk_Freq CONFIG.ADC2_Sampling_Rate CONFIG.ADC3_Band CONFIG.ADC3_Clock_Dist CONFIG.ADC3_Clock_Source CONFIG.ADC3_Clock_Source_MX CONFIG.ADC3_Enable CONFIG.ADC3_Fabric_Freq CONFIG.ADC3_Link_Coupling CONFIG.ADC3_Multi_Tile_Sync CONFIG.ADC3_OBS_Fabric_Freq CONFIG.ADC3_Outclk_Freq CONFIG.ADC3_PLL_Enable CONFIG.ADC3_Refclk_Div CONFIG.ADC3_Refclk_Freq CONFIG.ADC3_Sampling_Rate CONFIG.ADC224_En CONFIG.ADC225_En CONFIG.ADC226_En CONFIG.ADC227_En CONFIG.ADC_Bypass_BG_Cal00 CONFIG.ADC_Bypass_BG_Cal01 CONFIG.ADC_Bypass_BG_Cal02 CONFIG.ADC_Bypass_BG_Cal03 CONFIG.ADC_Bypass_BG_Cal10 CONFIG.ADC_Bypass_BG_Cal11 CONFIG.ADC_Bypass_BG_Cal12 CONFIG.ADC_Bypass_BG_Cal13 CONFIG.ADC_Bypass_BG_Cal20 CONFIG.ADC_Bypass_BG_Cal21 CONFIG.ADC_Bypass_BG_Cal22 CONFIG.ADC_Bypass_BG_Cal23 CONFIG.ADC_Bypass_BG_Cal30 CONFIG.ADC_Bypass_BG_Cal31 CONFIG.ADC_Bypass_BG_Cal32 CONFIG.ADC_Bypass_BG_Cal33 CONFIG.ADC_CalOpt_Mode00 CONFIG.ADC_CalOpt_Mode01 CONFIG.ADC_CalOpt_Mode02 CONFIG.ADC_CalOpt_Mode03 CONFIG.ADC_CalOpt_Mode10 CONFIG.ADC_CalOpt_Mode11 CONFIG.ADC_CalOpt_Mode12 CONFIG.ADC_CalOpt_Mode13 CONFIG.ADC_CalOpt_Mode20 CONFIG.ADC_CalOpt_Mode21 CONFIG.ADC_CalOpt_Mode22 CONFIG.ADC_CalOpt_Mode23 CONFIG.ADC_CalOpt_Mode30 CONFIG.ADC_CalOpt_Mode31 CONFIG.ADC_CalOpt_Mode32 CONFIG.ADC_CalOpt_Mode33 CONFIG.ADC_Coarse_Mixer_Freq00 CONFIG.ADC_Coarse_Mixer_Freq01 CONFIG.ADC_Coarse_Mixer_Freq02 CONFIG.ADC_Coarse_Mixer_Freq03 CONFIG.ADC_Coarse_Mixer_Freq10 CONFIG.ADC_Coarse_Mixer_Freq11 CONFIG.ADC_Coarse_Mixer_Freq12 CONFIG.ADC_Coarse_Mixer_Freq13 CONFIG.ADC_Coarse_Mixer_Freq20 CONFIG.ADC_Coarse_Mixer_Freq21 CONFIG.ADC_Coarse_Mixer_Freq22 CONFIG.ADC_Coarse_Mixer_Freq23 CONFIG.ADC_Coarse_Mixer_Freq30 CONFIG.ADC_Coarse_Mixer_Freq31 CONFIG.ADC_Coarse_Mixer_Freq32 CONFIG.ADC_Coarse_Mixer_Freq33 CONFIG.ADC_DSA_RTS CONFIG.ADC_Data_Type00 CONFIG.ADC_Data_Type01 CONFIG.ADC_Data_Type02 CONFIG.ADC_Data_Type03 CONFIG.ADC_Data_Type10 CONFIG.ADC_Data_Type11 CONFIG.ADC_Data_Type12 CONFIG.ADC_Data_Type13 CONFIG.ADC_Data_Type20 CONFIG.ADC_Data_Type21 CONFIG.ADC_Data_Type22 CONFIG.ADC_Data_Type23 CONFIG.ADC_Data_Type30 CONFIG.ADC_Data_Type31 CONFIG.ADC_Data_Type32 CONFIG.ADC_Data_Type33 CONFIG.ADC_Data_Width00 CONFIG.ADC_Data_Width01 CONFIG.ADC_Data_Width02 CONFIG.ADC_Data_Width03 CONFIG.ADC_Data_Width10 CONFIG.ADC_Data_Width11 CONFIG.ADC_Data_Width12 CONFIG.ADC_Data_Width13 CONFIG.ADC_Data_Width20 CONFIG.ADC_Data_Width21 CONFIG.ADC_Data_Width22 CONFIG.ADC_Data_Width23 CONFIG.ADC_Data_Width30 CONFIG.ADC_Data_Width31 CONFIG.ADC_Data_Width32 CONFIG.ADC_Data_Width33 CONFIG.ADC_Debug CONFIG.ADC_Decimation_Mode00 CONFIG.ADC_Decimation_Mode01 CONFIG.ADC_Decimation_Mode02 CONFIG.ADC_Decimation_Mode03 CONFIG.ADC_Decimation_Mode10 CONFIG.ADC_Decimation_Mode11 CONFIG.ADC_Decimation_Mode12 CONFIG.ADC_Decimation_Mode13 CONFIG.ADC_Decimation_Mode20 CONFIG.ADC_Decimation_Mode21 CONFIG.ADC_Decimation_Mode22 CONFIG.ADC_Decimation_Mode23 CONFIG.ADC_Decimation_Mode30 CONFIG.ADC_Decimation_Mode31 CONFIG.ADC_Decimation_Mode32 CONFIG.ADC_Decimation_Mode33 CONFIG.ADC_Dither00 CONFIG.ADC_Dither01 CONFIG.ADC_Dither02 CONFIG.ADC_Dither03 CONFIG.ADC_Dither10 CONFIG.ADC_Dither11 CONFIG.ADC_Dither12 CONFIG.ADC_Dither13 CONFIG.ADC_Dither20 CONFIG.ADC_Dither21 CONFIG.ADC_Dither22 CONFIG.ADC_Dither23 CONFIG.ADC_Dither30 CONFIG.ADC_Dither31 CONFIG.ADC_Dither32 CONFIG.ADC_Dither33 CONFIG.ADC_MTS_Variable_Fabric_Width CONFIG.ADC_Mixer_Mode00 CONFIG.ADC_Mixer_Mode01 CONFIG.ADC_Mixer_Mode02 CONFIG.ADC_Mixer_Mode03 CONFIG.ADC_Mixer_Mode10 CONFIG.ADC_Mixer_Mode11 CONFIG.ADC_Mixer_Mode12 CONFIG.ADC_Mixer_Mode13 CONFIG.ADC_Mixer_Mode20 CONFIG.ADC_Mixer_Mode21 CONFIG.ADC_Mixer_Mode22 CONFIG.ADC_Mixer_Mode23 CONFIG.ADC_Mixer_Mode30 CONFIG.ADC_Mixer_Mode31 CONFIG.ADC_Mixer_Mode32 CONFIG.ADC_Mixer_Mode33 CONFIG.ADC_Mixer_Type00 CONFIG.ADC_Mixer_Type01 CONFIG.ADC_Mixer_Type02 CONFIG.ADC_Mixer_Type03 CONFIG.ADC_Mixer_Type10 CONFIG.ADC_Mixer_Type11 CONFIG.ADC_Mixer_Type12 CONFIG.ADC_Mixer_Type13 CONFIG.ADC_Mixer_Type20 CONFIG.ADC_Mixer_Type21 CONFIG.ADC_Mixer_Type22 CONFIG.ADC_Mixer_Type23 CONFIG.ADC_Mixer_Type30 CONFIG.ADC_Mixer_Type31 CONFIG.ADC_Mixer_Type32 CONFIG.ADC_Mixer_Type33 CONFIG.ADC_NCO_Freq00 CONFIG.ADC_NCO_Freq01 CONFIG.ADC_NCO_Freq02 CONFIG.ADC_NCO_Freq03 CONFIG.ADC_NCO_Freq10 CONFIG.ADC_NCO_Freq11 CONFIG.ADC_NCO_Freq12 CONFIG.ADC_NCO_Freq13 CONFIG.ADC_NCO_Freq20 CONFIG.ADC_NCO_Freq21 CONFIG.ADC_NCO_Freq22 CONFIG.ADC_NCO_Freq23 CONFIG.ADC_NCO_Freq30 CONFIG.ADC_NCO_Freq31 CONFIG.ADC_NCO_Freq32 CONFIG.ADC_NCO_Freq33 CONFIG.ADC_NCO_Phase00 CONFIG.ADC_NCO_Phase01 CONFIG.ADC_NCO_Phase02 CONFIG.ADC_NCO_Phase03 CONFIG.ADC_NCO_Phase10 CONFIG.ADC_NCO_Phase11 CONFIG.ADC_NCO_Phase12 CONFIG.ADC_NCO_Phase13 CONFIG.ADC_NCO_Phase20 CONFIG.ADC_NCO_Phase21 CONFIG.ADC_NCO_Phase22 CONFIG.ADC_NCO_Phase23 CONFIG.ADC_NCO_Phase30 CONFIG.ADC_NCO_Phase31 CONFIG.ADC_NCO_Phase32 CONFIG.ADC_NCO_Phase33 CONFIG.ADC_NCO_RTS CONFIG.ADC_Neg_Quadrature00 CONFIG.ADC_Neg_Quadrature01 CONFIG.ADC_Neg_Quadrature02 CONFIG.ADC_Neg_Quadrature03 CONFIG.ADC_Neg_Quadrature10 CONFIG.ADC_Neg_Quadrature11 CONFIG.ADC_Neg_Quadrature12 CONFIG.ADC_Neg_Quadrature13 CONFIG.ADC_Neg_Quadrature20 CONFIG.ADC_Neg_Quadrature21 CONFIG.ADC_Neg_Quadrature22 CONFIG.ADC_Neg_Quadrature23 CONFIG.ADC_Neg_Quadrature30 CONFIG.ADC_Neg_Quadrature31 CONFIG.ADC_Neg_Quadrature32 CONFIG.ADC_Neg_Quadrature33 CONFIG.ADC_Nyquist00 CONFIG.ADC_Nyquist01 CONFIG.ADC_Nyquist02 CONFIG.ADC_Nyquist03 CONFIG.ADC_Nyquist10 CONFIG.ADC_Nyquist11 CONFIG.ADC_Nyquist12 CONFIG.ADC_Nyquist13 CONFIG.ADC_Nyquist20 CONFIG.ADC_Nyquist21 CONFIG.ADC_Nyquist22 CONFIG.ADC_Nyquist23 CONFIG.ADC_Nyquist30 CONFIG.ADC_Nyquist31 CONFIG.ADC_Nyquist32 CONFIG.ADC_Nyquist33 CONFIG.ADC_OBS00 CONFIG.ADC_OBS01 CONFIG.ADC_OBS02 CONFIG.ADC_OBS03 CONFIG.ADC_OBS10 CONFIG.ADC_OBS11 CONFIG.ADC_OBS12 CONFIG.ADC_OBS13 CONFIG.ADC_OBS20 CONFIG.ADC_OBS21 CONFIG.ADC_OBS22 CONFIG.ADC_OBS23 CONFIG.ADC_OBS30 CONFIG.ADC_OBS31 CONFIG.ADC_OBS32 CONFIG.ADC_OBS33 CONFIG.ADC_OBS_Data_Width00 CONFIG.ADC_OBS_Data_Width01 CONFIG.ADC_OBS_Data_Width02 CONFIG.ADC_OBS_Data_Width03 CONFIG.ADC_OBS_Data_Width10 CONFIG.ADC_OBS_Data_Width11 CONFIG.ADC_OBS_Data_Width12 CONFIG.ADC_OBS_Data_Width13 CONFIG.ADC_OBS_Data_Width20 CONFIG.ADC_OBS_Data_Width21 CONFIG.ADC_OBS_Data_Width22 CONFIG.ADC_OBS_Data_Width23 CONFIG.ADC_OBS_Data_Width30 CONFIG.ADC_OBS_Data_Width31 CONFIG.ADC_OBS_Data_Width32 CONFIG.ADC_OBS_Data_Width33 CONFIG.ADC_OBS_Decimation_Mode00 CONFIG.ADC_OBS_Decimation_Mode01 CONFIG.ADC_OBS_Decimation_Mode02 CONFIG.ADC_OBS_Decimation_Mode03 CONFIG.ADC_OBS_Decimation_Mode10 CONFIG.ADC_OBS_Decimation_Mode11 CONFIG.ADC_OBS_Decimation_Mode12 CONFIG.ADC_OBS_Decimation_Mode13 CONFIG.ADC_OBS_Decimation_Mode20 CONFIG.ADC_OBS_Decimation_Mode21 CONFIG.ADC_OBS_Decimation_Mode22 CONFIG.ADC_OBS_Decimation_Mode23 CONFIG.ADC_OBS_Decimation_Mode30 CONFIG.ADC_OBS_Decimation_Mode31 CONFIG.ADC_OBS_Decimation_Mode32 CONFIG.ADC_OBS_Decimation_Mode33 CONFIG.ADC_RESERVED_1_00 CONFIG.ADC_RESERVED_1_01 CONFIG.ADC_RESERVED_1_02 CONFIG.ADC_RESERVED_1_03 CONFIG.ADC_RESERVED_1_10 CONFIG.ADC_RESERVED_1_11 CONFIG.ADC_RESERVED_1_12 CONFIG.ADC_RESERVED_1_13 CONFIG.ADC_RESERVED_1_20 CONFIG.ADC_RESERVED_1_21...
        """        
