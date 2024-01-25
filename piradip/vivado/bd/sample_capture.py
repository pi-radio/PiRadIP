import math

from .hier import BDHier
from .pin import all_pins, create_pin
from .xilinx import *
from .piradio import *
from .rfdc import RFDC

class SampleCapture(BDHier):
    def __init__(self, parent, NCOFreq=1.25, name="data_capture",
                 complex_samples=True,
                 tx_samples=16384, rx_samples=32768):
        super().__init__(parent, name)

        #
        # Create IP blocks
        #
        print("Creating RFDC block...")
        self.rfdc = RFDC(self, "rfdc", NCOFreq=NCOFreq)
        print("Setting up ADC streams...")
        self.rfdc.setup_adc_axis()
        print("Setting up ADC I/Q interleaving...")
        self.rfdc.setup_interleave()
        print("Setting up DAC streams...")
        self.rfdc.setup_dac_axis()

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
            
        self.sample_out = [
            SampleBufferOut(self,
                            f"samples_out{i}",
                                {
                                    "CONFIG.C_AXIMM_ADDR_WIDTH": out_addr_width,
                                    "CONFIG.STREAM_OUT_WIDTH": 256
                                }) for i in range(8) ]

        self.sample_in = [
            AXISSampleBufferIn(self,
                               f"samples_in{i}",
                               {
                                    "CONFIG.C_AXIMM_ADDR_WIDTH": in_addr_width,
                                    "CONFIG.STREAM_IN_WIDTH": 256 
                               }) for i in range(8) ]


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
        self.rfdc.ext_reset_in.connect(self.ext_reset_in)

        self.not_resetn = BDVectorLogic(self, "not_resetn", { "CONFIG.C_OPERATION": "not", "CONFIG.C_SIZE": "1" })

        self.not_resetn.pins["Op1"].connect(self.pins["ext_reset_in"])

        for c in self.rfdc.adc_axis_clocks:
            c.pins["reset"].connect(self.not_resetn.pins["Res"])

        #
        # Make AXI connections
        #
        print("Connecting internal AXI busses...")
        self.axi_interconnect.aximm.connect(self.rfdc.pins["s_axi"])
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

            
            
        for net, soc in zip(self.rfdc.dac_axis_clk, all_pins(self.sample_out, "stream_out_clk")):
            net.connect(soc)
            
        for net, sor in zip(self.rfdc.dac_axis_resetn, all_pins(self.sample_out, "stream_out_resetn")):
            net.connect(sor)

        for sbo, dac_axis in zip(all_pins(self.sample_out, "STREAM_OUT"), self.rfdc.dac_axis):
            dac_axis.connect(sbo)


        for net, sic in zip(self.rfdc.adc_axis_clk, all_pins(self.sample_in, "stream_in_clk")):
            net.connect(sic)
            
        for net, sir in zip(self.rfdc.adc_axis_resetn, all_pins(self.sample_in, "stream_in_resetn")):
            net.connect(sir)

        for i, (si, adc_axis) in enumerate(zip(all_pins(self.sample_in, "STREAM_IN"), self.rfdc.adc_axis)):
            adc_axis.connect(si)
            
        for i, (si, adci) in enumerate(zip(all_pins(self.sample_in, "i_en"), self.rfdc.i_en)):
            adci.connect(si)

        for i, (si, adci) in enumerate(zip(all_pins(self.sample_in, "q_en"), self.rfdc.q_en)):
            adci.connect(si)



        
        """
        self.connect(self.axi_aclk,
                     *self.axi_interconnect.clk_pins,
                     *all_pins(self.sample_out, "aximm_clk"),
                     *all_pins(self.sample_in, "aximm_clk"),
                     *all_pins(self.sample_out, "axilite_clk"),
                     *all_pins(self.sample_in, "axilite_clk"),
                     self.trigger.pins["axilite_clk"],
                     self.rfdc.pins["s_axi_aclk"])

        self.connect(self.axi_rstn,
                     *self.axi_interconnect.rst_pins,
                     *all_pins(self.sample_out, "aximm_resetn"),
                     *all_pins(self.sample_in, "aximm_resetn"),
                     *all_pins(self.sample_out, "axilite_resetn"),
                     *all_pins(self.sample_in, "axilite_resetn"),
                     self.trigger.pins["axilite_resetn"],
                     self.rfdc.pins["s_axi_aresetn"])
        """
