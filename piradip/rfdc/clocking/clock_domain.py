from functools import cached_property

from piradip.vivado.bd.ip import BDIP
from piradip.vivado.bd.hier import BDHier
from piradip.vivado.bd.pin import BDIntfPin, all_pins, create_pin
from piradip.vivado.bd.xilinx import BDPSReset, ClockWizard, BDVectorLogic
from piradip.vivado.bd.axis import AXISDataWidthConverter, AXISClockConverter
from piradip.vivado.bd.piradio import AXISSampleInterleaver

class DCClockDomain:
    def __init__(self, rfdc, dctype, ref_clk):
        print(f"Creating clock domain for {ref_clk.name}")
        domain = ref_clk.name[-4:]
        
        self.rfdc = rfdc
        self.n = int(domain[-1])
        self.dctype = dctype
        self.ref_clk = ref_clk


        self.setup_clock()

        self.clk.pins["clk_in1"].connect(ref_clk)
        
        self.setup_reset()

        self.ext_axis_clk_pin = create_pin(self.rfdc, name=f"{self.pin_prefix}_aclk", direction="O", pin_type="clk")
        self.ext_axis_clk_pin.create()
        self.ext_axis_clk_pin.connect(self.ext_axis_clk)

        self.ext_axis_rst_pin = create_pin(self.rfdc, name=f"{self.pin_prefix}_aresetn", direction="O", pin_type="rst")
        self.ext_axis_rst_pin.create()
        self.ext_axis_rst_pin.connect(self.resetn)
        
        
    def setup_reset(self):
        self.reset_block = BDPSReset(self.rfdc, f"{self.dctype}_reset_{self.n}", None)

        self.resetn = self.create_net(None, "resetn")
        
        self.reset_block.pins["ext_reset_in"].connect(self.rfdc.resetn)
        self.reset_block.pins["dcm_locked"].connect(self.clk.pins["locked"])            
        self.reset_block.pins["slowest_sync_clk"].connect(self.reset_clk)

        self.resetn.connect(self.reset_block.pins["peripheral_aresetn"])

    def create_net(self, intf, name):
        return self.rfdc.create_net(intf, f"{self.dctype}{self.n}_{name}")

class ADCClockDomain(DCClockDomain):
    def __init__(self, rfdc, ref_clk):
        super().__init__(rfdc, "adc", ref_clk)

class DACClockDomain(DCClockDomain):
    def __init__(self, rfdc, ref_clk):
        super().__init__(rfdc, "dac", ref_clk)
