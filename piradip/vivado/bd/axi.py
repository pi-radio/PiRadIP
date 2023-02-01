import re

from .ip import BDIP

def is_aximm(p):
    try:
        return p.vlnv == "xilinx.com:interface:aximm_rtl:1.0"
    except AttributeError:
        return False
    
sequence_re = re.compile(".*[\D](?P<seq>[\d]+)")

    
class AXIMMIface:
    @classmethod
    def wrap(cls, other):
        if isinstance(other, AXIMMIface):
            return other
        
        if other.intf:
            if hasattr(other, "aximm"):
                return other.aximm
            else:
                try:
                    ovr = other.parent.aximm_overrides[other.name]

                    return AXIMMIface(other, clk=other.pins[ovr["clk"]], rst=other.pins[ovr["rst"]])
                except AttributeError:
                    pass
                except KeyError:
                    pass

                return AXIMMIface(other)

        raise RuntimeError(f"AXIMM: Unable to wrap {other}")

        
    def __init__(self, iface, **kwargs):
        self.iface = iface
        iface.aximm = self

        parent = iface.parent
        
        name = self.iface.name.upper()

        if "_" in name:
            prefix = name[:name.rindex("_")+1]
        else:
            prefix = name + "_"
            
        m = sequence_re.match(name)

        if m is not None:        
            self.seq = int(m["seq"])
        else:
            self.seq = 1000000

        def get_param(s):
            if s in kwargs:
                return kwargs[s]

            try:
                override = parent.aximm_overrides[iface.name][s]
            except AttributeError:
                pass
            else:
                return override

            l0 = list(parent.clk_pins if s == "clk" else parent.rst_pins)
            
            l = list(filter(lambda p: p.name.upper().startswith(prefix), l0))
            assert len(l) == 1, f"{parent.name}: Invalid clock pin config: {self.iface.name} found: {l} {l0}"
            return l[0]

        self.clk = get_param("clk")
        self.rst = get_param("rst")

    @property
    def mode(self):
        return self.iface.mode

    def connect(self, other):
        assert not self.iface.connected, f"{self.iface.name} already connected: {self.iface.net.name} {self.iface.net.pins}"

        other = self.wrap(other)

        self.rst.connect(other.rst)
        self.clk.connect(other.clk)
        self.iface.connect(other.iface)

        return self

    def debug(self):
        debug_args = {
            "AXI_R_ADDRESS": "Data and Trigger",
            "AXI_R_DATA": "Data and Trigger",
            "AXI_W_ADDRESS": "Data and Trigger",
            "AXI_W_DATA": "Data and Trigger",
            "AXI_W_RESPONSE": "Data and Trigger",
            "CLK_SRC": "/ps/pl_clk0",
            "SYSTEM_ILA": "Auto",
            "APC_EN": "1"
        }
        
        print(self.iface.net)
        self.iface.cmd(f"set_property HDL_ATTRIBUTE.DEBUG true {self.iface.outer_net.obj}")
        self.iface.cmd(f"apply_bd_automation -rule xilinx.com:bd_rule:debug" +
                       f" -dict [list {self.iface.outer_net.obj}" +
                       f' {{AXI_R_ADDRESS "Data and Trigger"' +
                       f' AXI_R_DATA "Data and Trigger"' +
                       f' AXI_W_ADDRESS "Data and Trigger"' +
                       f' AXI_W_DATA "Data and Trigger"' +
                       f' AXI_W_RESPONSE "Data and Trigger"' +
                       f' CLK_SRC "/ps/pl_clk0"' +
                       f' SYSTEM_ILA "Auto"' +
                       f' APC_EN "1" }} ]')
        
        
class AXIMMWrapper:
    def __init__(self, obj):
        self.obj = obj
        
        self.all_pins = [ AXIMMIface(p) for p in obj.pins.values() if is_aximm(p) ]
        
        self.obj.aximm = self

        self.m = { p.iface.name: p for p in filter(lambda p: p.iface.mode == 'Master', self.all_pins) }
        self.s = { p.iface.name: p for p in filter(lambda p: p.iface.mode == 'Slave', self.all_pins) }

        self.miter = iter(sorted(filter(lambda p: hasattr(p, "seq"), self.m.values()), key=lambda p: p.seq))
        self.siter = iter(sorted(filter(lambda p: hasattr(p, "seq"), self.m.values()), key=lambda p: p.seq))

    def connect(self, other):
        # Connect the first appropriate type
        other = AXIMMIface.wrap(other)

        if other.iface.mode == 'Master':
            i = next(self.siter)
        elif other.iface.mode == 'Slave':
            i = next(self.miter)

        return i.connect(other)
            
        
@BDIP.register
class AXIInterconnect(BDIP):
    vlnv = "xilinx.com:ip:axi_interconnect:2.1"

    def __init__(self, parent, name, **kwargs):
        p = dict()

        assert not ("num_masters" in kwargs and "num_managers" in kwargs), "Can not specify both managers and masters."
        assert not ("num_slaves" in kwargs and "num_subordinates" in kwargs), "Can not specify both subordinates and slaves."

        assert (("global_clock" in kwargs) == ("global_reset" in kwargs)), "Both clock and reset must be specified to use globally"
        
        if "num_masters" in kwargs:
            p["CONFIG.NUM_MI"] = kwargs["num_masters"]
        elif "num_managers" in kwargs:
            p["CONFIG.NUM_MI"] = kwargs["num_managers"]

            
        if "num_slaves" in kwargs:
            p["CONFIG.NUM_SI"] = kwargs["num_slaves"]
        elif "num_subordinates" in kwargs:
            p["CONFIG.NUM_SI"] = kwargs["num_subordinates"]
            
        super().__init__(parent, name, p)

        if "global_clock" in kwargs:
            AXIMMWrapper(self)

            self.parent.connect(kwargs["global_clock"], *[ p.clk for p in self.aximm.all_pins ])
            self.parent.connect(kwargs["global_reset"], *[ p.rst for p in self.aximm.all_pins ])
            

    @property
    def num_subordinates(self):
        return int(self.get_property("CONFIG.NUM_SI"))
