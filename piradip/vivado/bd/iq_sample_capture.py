import math

from .hier import BDHier
from .pin import all_pins, create_pin
from .xilinx import *
from .sample_buffer import *
from .piradio import *
from piradip.rfdc import RFDCIQ

class IQSampleCapture(BDHier):
    def __init__(self, parent, NCOFreq=1.25, name="data_capture",
                 complex_samples=True,
                 tx_samples=16384, rx_samples=32768,
                 sample_freq=4e9, reclock_adc=True):                 
        super().__init__(parent, name)

        #
        # Create IP blocks
        #
        print("Creating RFDC block...")
        self.rfdc = RFDCIQ(self, "rfdc", sample_freq=sample_freq, reclock_adc=False) #NCOFreq=NCOFreq)

        # Assumes complex samples
        if complex_samples:
            out_addr_width = math.log2(tx_samples) + 2
            in_addr_width = math.log2(rx_samples) + 2
        else:
            out_addr_width = math.log2(tx_samples) + 1
            in_addr_width = math.log2(rx_samples) + 1

        out_addr_width = int(out_addr_width)
        in_addr_width = int(in_addr_width)
            
        print(f"Configuring tx sample capture with {1 << out_addr_width} bytes")
        print(f"Configuring rx sample capture with {1 << in_addr_width} bytes")
            
        nwords = []

        def sample_config(x):
            print(x)
            if type(x) == dict:                
                return { ('nwords' if k=='n' else k):(v // 2 if k=='n' else v) for k, v in x.items() }
            
            return { 'nwords': x // 2 }
            
        try:
            sample_iter = iter(tx_samples)
        except:
            sample_iter = [ tx_samples for i in range(8) ]

        sbo_config = [ sample_config(i) for i in sample_iter ]

        try:
            sample_iter = iter(rx_samples)
        except:
            sample_iter = [ rx_samples for i in range(8) ]

        sbi_config = [ sample_config(i) for i in sample_iter ]

        
        self.sample_out = [
            SampleBufferOut(self, f"samples_out{i}", 256,
                            **v) for i, v in enumerate(sbo_config)
        ]

        
        self.sample_in = [
            SampleBufferIn(self, f"samples_in{i}", 256,
                            **v) for i, v in enumerate(sbi_config)
        ]


        self.trigger = TriggerUnit(self, "trigger", None)
        self.slice32 = Slice32(self, "trigger_slice", None)

        # Clock and reset inputs
        self.axi_aclk = create_pin(self, "s_axi_aclk", pin_type="clk").create()
        self.axi_rstn = create_pin(self, "s_axi_aresetn", pin_type="rst").create()
        
        self.axi_interconnect = AXIInterconnect(self, "axi_fabric", num_masters=34,
                                                global_clock=self.pins["s_axi_aclk"],
                                                global_reset=self.pins["s_axi_aresetn"])            

        
        #
        # Create external interfaces
        #
        print("Creating external interfaces...")
        self.external_interfaces = list()
        self.external_clocks = list()

        if False:
            for p in self.rfdc.adc_clk + self.rfdc.dac_clk:
                np = self.reexport(p)
                self.external_interfaces.append(np)
                self.external_clocks.append(np)

            for p in self.rfdc.adc_in + self.rfdc.dac_out + [ self.rfdc.sysref_in ]:
                np = self.reexport(p)
                self.external_interfaces.append(np)

        self.ext_reset_in = create_pin(self, "ext_reset_in", pin_type="rst").create()
        self.irq = create_pin(self, "irq", direction="O", pin_type="intr").create()

        self.aximm_overrides = { "S00_AXI": { "clk": self.pins["s_axi_aclk"], "rst": self.pins["s_axi_aresetn"] } }

        print("Exporting AXI...")
        self.reexport(self.axi_interconnect.pins["S00_AXI"])
        
        #
        # Make internal connections
        #

        self.axi_aclk.connect(self.axi_interconnect.pins["ACLK"])
        self.axi_rstn.connect(self.axi_interconnect.pins["ARESETN"])
        
        #
        # Make external async reset connections
        #
        print("Connecting async resets...")
        self.ext_reset_in.connect(self.rfdc.resetn)

        self.not_resetn = BDVectorLogic(self, "not_resetn", { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": "1" })

        self.not_resetn.pins["Op1"].connect(self.pins["ext_reset_in"])

        #
        # Make AXI connections
        #
        print("Connecting internal AXI busses...")
        self.axi_interconnect.aximm.connect(self.rfdc.pins["S_AXI"])
        self.axi_interconnect.aximm.connect(self.trigger.pins["AXILITE"])

        for i in self.sample_in:
            self.axi_interconnect.aximm.connect(i.pins["AXILITE"])
            self.axi_interconnect.aximm.connect(i.pins["AXIMM"])
        
        for i in self.sample_out:
            self.axi_interconnect.aximm.connect(i.pins["AXILITE"])
            self.axi_interconnect.aximm.connect(i.pins["AXIMM"])

        print("Connecting trigger...")
        print(self.slice32.pins)
        self.connect(self.trigger.pins["triggers"], self.slice32.pins["din"])

        for i in range(8):
            self.connect(self.slice32.pins[f"dout{i}"], self.sample_out[i].pins["trigger"])

        for i in range(8):
            self.connect(self.slice32.pins[f"dout{8+i}"], self.sample_in[i].pins["trigger"])

        for i, sbi in enumerate(self.sample_in):
            self.connect(sbi.pins["i_en"], self.rfdc.pins[f"i{i}_en"])
            self.connect(sbi.pins["q_en"], self.rfdc.pins[f"q{i}_en"])
            
            
        for net, soc in zip(self.rfdc.dac_axis_clk, all_pins(self.sample_out, "stream_out_clk")):
            soc.connect(net)
            
        for net, sor in zip(self.rfdc.dac_axis_resetn, all_pins(self.sample_out, "stream_out_resetn")):
            sor.connect(net)

        for sbo, dac_axis in zip(all_pins(self.sample_out, "STREAM_OUT"), self.rfdc.dac_axis):
            sbo.connect(dac_axis)


        for net, sic in zip(self.rfdc.adc_axis_clk, all_pins(self.sample_in, "stream_in_clk")):
            sic.connect(net)
            
        for net, sir in zip(self.rfdc.adc_axis_resetn, all_pins(self.sample_in, "stream_in_resetn")):
            sir.connect(net)

        for i, (si, adc_axis) in enumerate(zip(all_pins(self.sample_in, "STREAM_IN"), self.rfdc.adc_axis)):
            si.connect(adc_axis)

