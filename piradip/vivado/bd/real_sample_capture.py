import math

from .hier import BDHier
from .pin import all_pins, create_pin
from .xilinx import *
from .sample_buffer import *
from .piradio import *
from piradip.rfdc import RFDCReal

class RealSampleCapture(BDHier):
    def __init__(self, parent, name="data_capture",
                 tx_samples=32768, rx_samples=32768,
                 sample_freq=4e9, reclock_adc=True):
        super().__init__(parent, name)

        #
        # Create IP blocks
        #
        print("Creating RFDC block...")
        self.rfdc = RFDCReal(self, "rfdc", sample_freq=sample_freq, reclock_adc=reclock_adc)

        
        #print(f"Configuring tx sample capture with {2*tx_samples} bytes (bus_width: {out_addr_width})")
        #print(f"Configuring rx sample capture with {1 << in_addr_width} bytes (bus_width: {in_addr_width})")

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

        self.filter_out = [
            AXIS_FIR7SYM_16WIDE(self,
                                f"filter_out{i}",
                                { "CONFIG.STREAM_IN_WIDTH": "256",
                                  "CONFIG.STREAM_OUT_WIDTH": "256" }) for i, _ in enumerate(sbo_config)
        ]

        self.trigger = TriggerUnit(self, "trigger", None)
        self.slice32 = Slice32(self, "trigger_slice", None)

        # Clock and reset inputs
        self.axi_aclk = create_pin(self, "s_axi_aclk", pin_type="clk").create()
        self.axi_rstn = create_pin(self, "s_axi_aresetn", pin_type="rst").create()

        print(f"Creating AXI fabric heirarchy...") 

        n_dac_tiles = 2
        n_dac_dc_per_tile = 4
        
        n_adc_tiles = 4
        n_adc_dc_per_tile = 2

        # Filter + SBO control + SBO mem
        n_dac_axi_units = 3

        # SBI control + SBI mem
        n_adc_axi_units = 2
                
        #
        # The plus two is for the trigger unit and the RFDC
        #
        self.axi_root = AXIInterconnect(self, "axi_fabric", num_masters=n_dac_tiles + n_adc_tiles + 2,
                                        global_clock=self.pins["s_axi_aclk"],
                                        global_reset=self.pins["s_axi_aresetn"])            

        self.axi_root.aximm.connect(self.rfdc.pins["S_AXI"])
        self.axi_root.aximm.connect(self.trigger.pins["AXILITE"])

        
        self.axi_dac_tiles = [ AXIInterconnect(self, f"axi_fabric_dac{i}",
                                               manager_regslice=True,
                                               num_masters=n_dac_dc_per_tile * n_dac_axi_units,
                                               global_master_clock=self.pins["s_axi_aclk"],
                                               global_master_reset=self.pins["s_axi_aresetn"])
                               for i in range(n_dac_tiles) ]

        self.axi_adc_tiles = [ AXIInterconnect(self, f"axi_fabric_adc{i}",
                                               manager_regslice=True,
                                               num_masters=n_adc_dc_per_tile * n_adc_axi_units,
                                               global_master_clock=self.pins["s_axi_aclk"],
                                               global_master_reset=self.pins["s_axi_aresetn"])
                               for i in range(n_adc_tiles) ]


        print("Connecting internal AXI heirarchy busses...")

        self.axi_root.pins["ACLK"].connect(self.pins["s_axi_aclk"])
        self.axi_root.pins["ARESETN"].connect(self.pins["s_axi_aresetn"])
        
        for adt in self.axi_dac_tiles:
            adt.pins["ACLK"].connect(self.pins["s_axi_aclk"])
            adt.pins["ARESETN"].connect(self.pins["s_axi_aresetn"])
            
            self.axi_root.aximm.connect(adt.pins["S00_AXI"])

        for aat in self.axi_adc_tiles:
            aat.pins["ACLK"].connect(self.pins["s_axi_aclk"])
            aat.pins["ARESETN"].connect(self.pins["s_axi_aresetn"])

            self.axi_root.aximm.connect(aat.pins["S00_AXI"])

            
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
        self.reexport(self.axi_root.pins["S00_AXI"])

        
        #
        # Make external async reset connections
        #
        print("Connecting async resets...")
        self.ext_reset_in.connect(self.rfdc.resetn)

        dtl = [ self.axi_dac_tiles[i] for i in range(2) for j in range(4) ]
        atl = [ self.axi_adc_tiles[i] for i in range(4) for j in range(2) ]
        
        for adt, sbo, fo in zip(dtl, self.sample_out, self.filter_out):
            adt.aximm.connect(sbo.pins["AXILITE"])
            adt.aximm.connect(sbo.pins["AXIMM"])
            adt.aximm.connect(fo.pins["AXILITE"])

        for aat, sbi in zip(atl, self.sample_in):
            aat.aximm.connect(sbi.pins["AXILITE"])
            aat.aximm.connect(sbi.pins["AXIMM"])
        
            
        """
            
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

        for i in self.filter_out:
            self.axi_interconnect.aximm.connect(i.pins["AXILITE"])

        """
        
        print("Connecting trigger...")
        print(self.slice32.pins)
        self.connect(self.trigger.pins["triggers"], self.slice32.pins["din"])
        self.connect(self.irq, self.rfdc.irq)
        
        for i in range(8):
            self.connect(self.slice32.pins[f"dout{i}"], self.sample_out[i].pins["trigger"])

        for i in range(8):
            self.connect(self.slice32.pins[f"dout{8+i}"], self.sample_in[i].pins["trigger"])


        #
        # DAC Clocks
        #
            
        for net, soc in zip(self.rfdc.dac_axis_clk, all_pins(self.sample_out, "stream_out_clk")):
            soc.connect(net)

        for net, soc in zip(self.rfdc.dac_axis_clk, all_pins(self.filter_out, "stream_in_clk")):
            soc.connect(net)

        for net, soc in zip(self.rfdc.dac_axis_clk, all_pins(self.filter_out, "stream_out_clk")):
            soc.connect(net)

        #
        # DAC Resets
        #

            
        for net, sor in zip(self.rfdc.dac_axis_resetn, all_pins(self.sample_out, "stream_out_resetn")):
            sor.connect(net)

        for net, sor in zip(self.rfdc.dac_axis_resetn, all_pins(self.filter_out, "stream_in_resetn")):
            sor.connect(net)
            
        for net, sor in zip(self.rfdc.dac_axis_resetn, all_pins(self.filter_out, "stream_out_resetn")):
            sor.connect(net)

        #
        # DAC Data
        #
            
        for sbo_axis, filter_axis in zip(all_pins(self.sample_out, "STREAM_OUT"), all_pins(self.filter_out, "STREAM_IN")):
            filter_axis.connect(sbo_axis)


        for filter_axis, dac_axis in zip(all_pins(self.filter_out, "STREAM_OUT"), self.rfdc.dac_axis):
            filter_axis.connect(dac_axis)

        #
        # ADC Clocks
        #
            
        for net, sic in zip(self.rfdc.adc_axis_clk, all_pins(self.sample_in, "stream_in_clk")):
            sic.connect(net)

        #
        # ADC Resets
        #
            
        for net, sir in zip(self.rfdc.adc_axis_resetn, all_pins(self.sample_in, "stream_in_resetn")):
            sir.connect(net)

        #
        # ADC data 
        #
            
        for i, (si, adc_axis) in enumerate(zip(all_pins(self.sample_in, "STREAM_IN"), self.rfdc.adc_axis)):
            si.connect(adc_axis)


        bd_name = f"{self.bd.bitstream_name}_i"
            
        if False:
            #
            # DAC Bank 228
            #
            self.add_post_synthesis_command(f"create_pblock DACTILE0_LOGIC")
            self.add_post_synthesis_command(f"resize_pblock DACTILE0_LOGIC -add CLOCKREGION_X1Y4:CLOCKREGION_X5Y4")
            
            self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE0_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_dac0]] -clear_locs")
        
            for i in range(4):
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE0_LOGIC [get_cells [list {bd_name}/data_capture/samples_out{i}]] -clear_locs")
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE0_LOGIC [get_cells [list {bd_name}/data_capture/filter_out{i}]] -clear_locs")

            
            #
            # DAC Bank 229
            #
            self.add_post_synthesis_command(f"create_pblock DACTILE1_LOGIC")
            self.add_post_synthesis_command(f"resize_pblock DACTILE1_LOGIC -add CLOCKREGION_X1Y5:CLOCKREGION_X5Y5")
            
            self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE1_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_dac1]] -clear_locs")

            for i in range(4):
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE1_LOGIC [get_cells [list {bd_name}/data_capture/samples_out{i+4}]] -clear_locs")
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE1_LOGIC [get_cells [list {bd_name}/data_capture/filter_out{i+4}]] -clear_locs")
        else:
            self.add_post_synthesis_command(f"create_pblock DACTILE_LOGIC")
            self.add_post_synthesis_command(f"resize_pblock DACTILE_LOGIC -add CLOCKREGION_X1Y4:CLOCKREGION_X5Y4")
            self.add_post_synthesis_command(f"resize_pblock DACTILE_LOGIC -add CLOCKREGION_X1Y5:CLOCKREGION_X5Y5")
            self.add_post_synthesis_command(f"resize_pblock DACTILE_LOGIC -add CLOCKREGION_X1Y6:CLOCKREGION_X5Y6")
            
            self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_dac0]] -clear_locs")
            self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_dac1]] -clear_locs")
        
            for i in range(8):
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE_LOGIC [get_cells [list {bd_name}/data_capture/samples_out{i}]] -clear_locs")
                self.add_post_synthesis_command(f"add_cells_to_pblock DACTILE_LOGIC [get_cells [list {bd_name}/data_capture/filter_out{i}]] -clear_locs")
            

        #
        # ADC Bank 224
        #
        self.add_post_synthesis_command(f"create_pblock ADCTILE0_LOGIC")
        self.add_post_synthesis_command(f"resize_pblock ADCTILE0_LOGIC -add CLOCKREGION_X2Y0:CLOCKREGION_X5Y0")
        
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE0_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_adc0]] -clear_locs")

        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE0_LOGIC [get_cells [list {bd_name}/data_capture/samples_in0]] -clear_locs")
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE0_LOGIC [get_cells [list {bd_name}/data_capture/samples_in1]] -clear_locs")

        #
        # ADC Bank 225
        #
        self.add_post_synthesis_command(f"create_pblock ADCTILE1_LOGIC")
        self.add_post_synthesis_command(f"resize_pblock ADCTILE1_LOGIC -add CLOCKREGION_X2Y1:CLOCKREGION_X5Y1")
        
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE1_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_adc1]] -clear_locs")

        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE1_LOGIC [get_cells [list {bd_name}/data_capture/samples_in2]] -clear_locs")
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE1_LOGIC [get_cells [list {bd_name}/data_capture/samples_in3]] -clear_locs")
            
        #
        # ADC Bank 226
        #
        self.add_post_synthesis_command(f"create_pblock ADCTILE2_LOGIC")
        self.add_post_synthesis_command(f"resize_pblock ADCTILE2_LOGIC -add CLOCKREGION_X2Y2:CLOCKREGION_X5Y2")
        
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE2_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_adc2]] -clear_locs")

        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE2_LOGIC [get_cells [list {bd_name}/data_capture/samples_in4]] -clear_locs")
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE2_LOGIC [get_cells [list {bd_name}/data_capture/samples_in5]] -clear_locs")

        #
        # ADC Bank 227
        #
        self.add_post_synthesis_command(f"create_pblock ADCTILE3_LOGIC")
        self.add_post_synthesis_command(f"resize_pblock ADCTILE3_LOGIC -add CLOCKREGION_X2Y3:CLOCKREGION_X5Y3")
        
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE3_LOGIC [get_cells [list {bd_name}/data_capture/axi_fabric_adc3]] -clear_locs")

        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE3_LOGIC [get_cells [list {bd_name}/data_capture/samples_in6]] -clear_locs")
        self.add_post_synthesis_command(f"add_cells_to_pblock ADCTILE3_LOGIC [get_cells [list {bd_name}/data_capture/samples_in7]] -clear_locs")

        
