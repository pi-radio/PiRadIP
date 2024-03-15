from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic, IBUFDS, BUFG, BDAnd
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver, MTSClocking

from .clocking import RFDCClocking
from .clock_domain import ADCClockDomain, DACClockDomain

class MTSADCClockDomain:
    def __init__(self, mts, n):
        self.mts = mts
        self.n = n

    @property
    def rfdc(self):
        return self.mts.rfdc
        
    @property
    def rfdc_axis_clk(self):
        return self.mts.rfdc_adc_axis_clk

    @property
    def resetn(self):
        return self.mts.resetn 
    
class MTSDACClockDomain:
    def __init__(self, mts, n):
        self.mts = mts
        self.n = n
        
    @property
    def rfdc(self):
        return self.mts.rfdc
        
    @property
    def rfdc_axis_clk(self):
        return self.mts.rfdc_dac_axis_clk

    @property
    def resetn(self):
        return self.mts.resetn 
    
class RFDCClockingMTS(RFDCClocking):
    def update_rfdc_props(self, props):
        for i in range(4):
            props[f"CONFIG.ADC{i}_Multi_Tile_Sync"] = "true"

        for i in range(2):
            props[f"CONFIG.DAC{i}_Multi_Tile_Sync"] = "true"

    def pre_setup(self):
        self.rfdc.set_property(f"CONFIG.ADC0_Multi_Tile_Sync", "true")
        self.rfdc.set_property(f"CONFIG.DAC0_Multi_Tile_Sync", "true")
        
        self.pl_clk_ibufds = IBUFDS(self.rfdc, "pl_clk_buf")
        self.sysref_ibufds = IBUFDS(self.rfdc, "sysref_clk_buf")

        self.pl_clk_bufg = BUFG(self.rfdc, "pl_clk_bufg")

        self.pl_clk_ibufds.pins["IBUF_OUT"].connect(self.pl_clk_bufg.pins["BUFG_I"])

        ports = self.rfdc.make_external(self.pl_clk_ibufds.pins["CLK_IN_D"],
                                                 name="pl_clk_in")
        
        def order_diff_ports(ports):
            assert len(ports) == 2
            if ports[0].name[-2:] == "_p":
                return (ports[0], ports[1])
            else:
                return (ports[1], ports[0])

        self.pl_clk_in_p, self.pl_clk_in_n = order_diff_ports(ports)
            
        
        self.pl_clk_in_p.set_phys("AL16", "LVDS")
        self.pl_clk_in_n.set_phys("AL15", "LVDS")

        self.pl_clk_in_p.set_diff_term("TERM_100")
        self.pl_clk_in_p.set_property("CONFIG.FREQ_HZ", "102400000")

        self.rfdc.bd.add_clock(self.pl_clk_in_p, 1000/102.4)
        
        self.mts_sync = MTSClocking(self.rfdc, "mts_sync", None)
                        
        self.reset_block = BDPSReset(
            self.rfdc,
            f"rfdc_ps_reset",
            None)

        self.resetn = self.rfdc.create_net(None, "resetn")
        
        self.mts_sync.pins["pl_clk"].connect(self.pl_clk_bufg.pins["BUFG_O"])
        self.mts_sync.pins["sysref_in"].connect(self.sysref_ibufds.pins["IBUF_OUT"])

        self.mts_sync.pins["resetn"].connect(self.rfdc.resetn)
        self.mts_sync.pins["sysref_adc"].connect(self.rfdc.rfdc.pins["user_sysref_adc"])
        self.mts_sync.pins["sysref_dac"].connect(self.rfdc.rfdc.pins["user_sysref_dac"])
        
        self.rfdc_adc_axis_clk = self.rfdc.create_net(None, "rfdc_adc_axis_clk")
        self.rfdc_dac_axis_clk = self.rfdc.create_net(None, "rfdc_dac_axis_clk")
        self.reset_clk = self.rfdc_dac_axis_clk
        
        self.rfdc_adc_axis_clk.connect(self.mts_sync.pins["adc_clk"])
        self.rfdc_dac_axis_clk.connect(self.mts_sync.pins["dac_clk"])

        self.rfdc.clk_locked = self.rfdc.reexport(self.mts_sync.pins["locked"], "clk_locked")
        self.rfdc.clk_stopped = self.rfdc.reexport(self.mts_sync.pins["clk_in_stopped"], "clk_stopped")
        self.rfdc.clk_fb_stopped = self.rfdc.reexport(self.mts_sync.pins["clk_fb_stopped"], "clkfb_stopped")        
                
        ports = self.rfdc.make_external(self.sysref_ibufds.pins["CLK_IN_D"],
                                        name="pl_sysref_in")


        self.sysref_in_p, self.sysref_in_n = order_diff_ports(ports)
                
        self.sysref_in_p.set_phys("AK17", "LVDS")
        self.sysref_in_n.set_phys("AK16", "LVDS")
         
        self.sysref_in_p.set_diff_term("TERM_100")
               
        if self.rfdc.reclock_adc:
            self.ext_adc_axis_clk_pin = create_pin(self.rfdc, name=f"axis_aclk", direction="O", pin_type="clk")
            self.ext_adc_axis_clk_pin.create()
            self.ext_adc_axis_clk_pin.connect(self.rfdc_dac_axis_clk)

            self.ext_dac_axis_clk_pin = self.ext_adc_axis_clk_pin
        else:
            self.ext_adc_axis_clk_pin = create_pin(self.rfdc, name=f"adc_axis_aclk", direction="O", pin_type="clk")
            self.ext_adc_axis_clk_pin.create()
            self.ext_adc_axis_clk_pin.connect(self.rfdc_adc_axis_clk)

            self.ext_dac_axis_clk_pin = create_pin(self.rfdc, name=f"dac_axis_aclk", direction="O", pin_type="clk")
            self.ext_dac_axis_clk_pin.create()
            self.ext_dac_axis_clk_pin.connect(self.rfdc_dac_axis_clk)

        self.ext_axis_rst_pin = create_pin(self.rfdc, name=f"axis_aresetn", direction="O", pin_type="rst")
        self.ext_axis_rst_pin.create()
        self.ext_axis_rst_pin.connect(self.resetn)
        
        self.reset_block.pins["ext_reset_in"].connect(self.rfdc.resetn)
        self.reset_block.pins["aux_reset_in"].connect(self.rfdc.resetn)
        self.reset_block.pins["dcm_locked"].connect(self.mts_sync.pins["locked"])
        self.reset_block.pins["slowest_sync_clk"].connect(self.reset_clk)

        self.resetn.connect(self.reset_block.pins["peripheral_aresetn"])

        self.adc_domains = [ MTSADCClockDomain(self, i) for i in range(self.rfdc.ADC_TILES) ]
        self.dac_domains = [ MTSDACClockDomain(self, i) for i in range(self.rfdc.DAC_TILES) ]

        
    @property
    def rfdc_adc_axis_clks(self):
        return [ self.rfdc_adc_axis_clk for _ in range(self.rfdc.NADCS) ]

    @property
    def rfdc_dac_axis_clks(self):
        return [ self.rfdc_dac_axis_clk for _ in range(self.rfdc.NDACS) ]

    @property
    def ext_adc_axis_clks(self):
        return [ self.ext_adc_axis_clk_pin for _ in range(self.rfdc.NADCS) ]

    @property
    def ext_dac_axis_clks(self):
        return [ self.ext_dac_axis_clk_pin for _ in range(self.rfdc.NDACS) ]


    @property
    def adc_axis_clk(self):
        return self.ext_adc_axis_clks

    @property
    def dac_axis_clk(self):
        return self.ext_dac_axis_clks

    
    @property
    def adc_resets(self):
        return [ self.resetn for _ in range(self.rfdc.NADCS) ]
        
    @property
    def dac_resets(self):
        return [ self.resetn for _ in range(self.rfdc.NDACS) ]


    @property
    def adc_axis_resetn(self):        
        return [ self.ext_axis_rst_pin for _ in range(self.rfdc.NADCS) ]
        
    @property
    def dac_axis_resetn(self):
        return [ self.ext_axis_rst_pin for _ in range(self.rfdc.NDACS) ]

    
"""        
create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz:6.0 clk_wiz_0
create_bd_cell: Time (s): cpu = 00:00:09 ; elapsed = 00:00:08 . Memory (MB): peak = 9573.199 ; gain = 253.512 ; free physical = 13562 ; free virtual = 23522
endgroup
set_property -dict [list CONFIG.PRIM_IN_FREQ.VALUE_SRC USER] [get_bd_cells clk_wiz_0]
set_property -dict [list \
  CONFIG.CLKIN1_JITTER_PS {81.38} \
  CONFIG.CLKOUT1_JITTER {105.601} \
  CONFIG.CLKOUT1_PHASE_ERROR {152.361} \
  CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {512.000} \
  CONFIG.CLKOUT2_JITTER {117.795} \
  CONFIG.CLKOUT2_PHASE_ERROR {152.361} \
  CONFIG.CLKOUT2_REQUESTED_OUT_FREQ {256} \
  CONFIG.CLKOUT2_USED {true} \
  CONFIG.MMCM_CLKFBOUT_MULT_F {31.250} \
  CONFIG.MMCM_CLKIN1_PERIOD {8.138} \
  CONFIG.MMCM_CLKOUT0_DIVIDE_F {2.500} \
  CONFIG.MMCM_CLKOUT1_DIVIDE {5} \
  CONFIG.MMCM_DIVCLK_DIVIDE {3} \
  CONFIG.NUM_OUT_CLKS {2} \
  CONFIG.PRIM_IN_FREQ {122.88} \
  CONFIG.PRIM_SOURCE {Differential_clock_capable_pin} \
] [get_bd_cells clk_wiz_0]
"""
