import math

from .hier import BDHier
from .pin import all_pins, create_pin
from .xilinx import *
from .sample_buffer import *
from .piradio import *
from piradip.rfdc import RFDCIQ


class SampleCapture(BDHier):
    def __init__(self, parent, NCOFreq=1.25, name="data_capture",
                 complex_samples=True,
                 tx_samples=16384, rx_samples=32768,
                 sample_freq=4e9, reclock_adc=True):                 
        pass
