from pathlib import Path
from functools import cached_property

from .axi import AXIInterconnect

class BDAddressSpace:
    def __init__(self, mapper, iface):
        self.mapper = mapper
        self.iface = iface
        self.children = list()

        self.dest_iface = iface.other
        self.dest_block = self.dest_iface.parent

        if not hasattr(self.iface, "address_spaces"):
            self.iface.address_spaces = list()

        if not hasattr(self.dest_iface, "address_spaces"):
            self.dest_iface.address_spaces = list()
        
        if not hasattr(self.dest_block, "address_spaces"):
            self.dest_block.address_spaces = list()

        self.dest_iface.address_spaces.append(self)
        self.dest_block.address_spaces.append(self)
            
        if self.dest_block.vlnv == AXIInterconnect.vlnv and len(self.dest_block.address_spaces) == 1:
            master_ifaces = filter(lambda x: x.vlnv == "xilinx.com:interface:aximm_rtl:1.0" and x.mode == "Master", self.dest_block.intf_pins)

            for m in master_ifaces:
                if hasattr(m, "address_space"):
                    continue
                self.children.append(BDAddressSpace(self.mapper, m))

    def map(self, base_addr):
        if self.dest_block.vlnv == AXIInterconnect.vlnv:
            for c in self.children:
                base_addr = c.map(base_addr)
        else:
            if hasattr(self, "base_addr"):
                return base_addr

            assert len(self.children) == 0

            aximm = self.dest_iface.path
            

            pin = None
                
            for p in self.iface.cmd(f"get_bd_pins -of_objects [get_bd_intf_pins {aximm}]").split():
                if p.endswith("_awaddr"):
                    pin = p
                    break

            if pin is None:
                raise RuntimeError(f"Could not find awaddr pin for interface {aximm}")

            left = int(self.iface.cmd(f"get_property LEFT [get_bd_pins {pin}]"))
            right = int(self.iface.cmd(f"get_property RIGHT [get_bd_pins {pin}]"))

            print(f"{pin} {left} {right}")

            self.required = 1 << (left + 1)

            if self.required < (1 << 16):
                self.required = 1 << 16
            
            addr_seg = self.iface.cmd(f"get_bd_addr_segs {aximm}/*").split()
            
            for seg in addr_seg:
                required = self.required

                print(f"seg: {seg} req: {required:08x} base_addr: {base_addr:08x}")
                
                if base_addr & (required - 1):
                    base_addr = (base_addr + required) & ~(required-1)
                
                self.base_addr = base_addr

                self.log(f"Mapping {seg} to 0x{base_addr:08x}")

                self.iface.cmd(f"assign_bd_address -offset 0x{self.base_addr:08x} -range 0x{self.required:x} " +
                               f"[get_bd_addr_segs {seg}]")

                base_addr += self.required

        return base_addr

                
    @cached_property
    def required(self):
        if len(self.children) == 0:
            # Yeah, find a way to figure this out -- Works For Now
            return self.dest_block.memory_aperture_size

        required = 0
        
        for c in self.children:
            required += c.required 

        return required

    def log(self, s):
        print(s)
        print(s, file=self.mapper.logfile)
    
class BDMemoryMapper:
    def __init__(self, bd, root):
        self.bd = bd
        self.root = root
        self.logfile = open(self.bd.logs / "memory_map", "w")
        
        self.root_spaces = list()
                 
        ifaces = filter(lambda x: x.vlnv == "xilinx.com:interface:aximm_rtl:1.0", self.root.intf_pins)

        for i in ifaces:
            print(f"Inspecting {i.path}")
            if i.mode == "Master":
                self.root_spaces.append(BDAddressSpace(self, i))
            elif i.mode == "Slave":
                print("Whistling and ignoring slave space.  Don't mind us...")
            else:
                assert False, "Yeah, this is just *wrong*"

        ba = 0xA0000000
        for rs in self.root_spaces:
            rs.map(ba)
        
