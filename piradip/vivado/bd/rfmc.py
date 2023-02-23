
class IOBank:
    def __init__(self, bank_no, bank_type):
        self.bank_no = bank_no
        self.bank_type = bank_type

def bank_set(*args):
    return { bank.bank_no : bank for bank in args }

class PackagePin:
    def __init__(self, ball, bank=None):
        self.ball = ball
        self.bank = bank

    @property
    def Ball(self):
        return self.ball
    
class ZCU111:
    banks = bank_set(IOBank(87, "HD"),
                     IOBank(84, "HD"))
        
        
class RFMC:
    class ADC:
        IO_00 = PackagePin("AP5")
        IO_01 = PackagePin("AP6")
        IO_02 = PackagePin("AR6")
        IO_03 = PackagePin("AR7")
        IO_04 = PackagePin("AV7")
        IO_05 = PackagePin("AU7")
        IO_06 = PackagePin("AV8")
        IO_07 = PackagePin("AU8")
        IO_08 = PackagePin("AT6")
        IO_09 = PackagePin("AT7")
        IO_10 = PackagePin("AU5")
        IO_11 = PackagePin("AT5")
        IO_12 = PackagePin("AU3")
        IO_13 = PackagePin("AU4")
        IO_14 = PackagePin("AV5")
        IO_15 = PackagePin("AV6")
        IO_16 = PackagePin("AU1")
        IO_17 = PackagePin("AU2")
        IO_18 = PackagePin("AV2")
        IO_19 = PackagePin("AV3")
            
    class DAC:
        class IO_00:
            Ball = "A9"
        class IO_01:
            Ball = "A10"
        class IO_02:
            Ball = "A6"
        class IO_03:
            Ball = "A7"
        class IO_04:
            Ball = "A5"
        class IO_05:
            Ball = "B5"
        class IO_06:
            Ball = "C5"
        class IO_07:
            Ball = "C6"
        class IO_08:
            Ball = "B9"
        class IO_09:
            Ball = "B10"
        class IO_10:
            Ball = "B7"
        class IO_11:
            Ball = "B8"
        class IO_12:
            Ball = "D8"
        class IO_13:
            Ball = "D9"
        class IO_14:
            Ball = "C7"
        class IO_15:
            Ball = "C8"
        class IO_16:
            Ball = "C10"
        class IO_17:
            Ball = "D10"
        class IO_18:
            Ball = "D6"
        class IO_19:
            Ball = "E7"
