from .process import VivadoMessageHandler
from collections import defaultdict, deque
import re

# 

class SynthesisMessageHandler(VivadoMessageHandler):
    ignore = {
        (8, 113):  0,   # 'binding component instance'...
        (1, 1174): 0,  # 'XPM XDC files'
        (8, 802):  0,   # Inferred FSM
        (8, 7079): 0,  # Multithreading
        (8, 7078): 0,  # Launching helper
        (8, 7075): 0,  # Helper process
        
        # Maybe useful?
        (8, 226):  10,   # 'default block is never used'...
        (8, 7030): 10,  # Implemented non-cascaded BRAM
        (8, 3332): 10,  # Sequential element
        (8, 5544): 10,  # ROM too small for BRAM
        (8, 3491): 10,  # bound to instance
        (8, 6014): 10,  # Unused sequential
        (8, 5396): 10,  # clock with keep attribute
        (8, 5578): 10,  # Moved timing constraint
        (8, 7067): 10,  # Removed DRAM instance
        (8, 6904): 10,  # IMplemented with LUTRAM
        (8, 3886): 10,  # merging instance
        (8, 3354): 10,  # FSM encoding
    }

    highlight = {
        (8, 87): 100, # Did *not* result in combanitorical logic
        (8, 327): 100, # Inferred latch
    }
    

    def __init__(self, wrapper):
        super().__init__(wrapper, [ "Synth" ])

        # file -> level -> lines -> maj, min -> msgs
        self.file_msgs = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(
                    lambda: defaultdict(list)
                )
            )
        )

        self.seen = set()
        self.important_msgs = list()
        self.modules = defaultdict(lambda: { 'file': None, 'line': None, 'synthesizing': False, 'messages': list() })

    def end_report(self):
        print("Highlighted messages:")
        for m in self.important_msgs:
            print(m)
        
    def handle_msg(self, msg):
        assert msg.facility == "Synth"

        if msg.msg.find("IBUF") != -1:
            print(f"IBUF: {msg}")
        
        if msg.number in self.ignore:
            return True

        if msg.msg.startswith("synthesizing"):
            self.modules[msg.module]['file'] = msg.filename
            self.modules[msg.module]['line'] = msg.line
            self.modules[msg.module]['synthesizing'] = True
            print(f"Synthesizing {msg.module}...")
            return True
        elif msg.msg.startswith("done synthesizing"):
            print(f"Done with {msg.module}...")
            #assert self.modules[msg.module]['synthesizing'], f"{msg.module} marked as done {self.modules[msg.module]}"
            if not self.modules[msg.module]['synthesizing']:
                print(f"Never saw open for {msg.module}")
            self.modules[msg.module]['synthesizing'] = False
            return True
        elif msg.msg.find("synth") != -1:
            print(f"NOT SYNTH: |{msg.msg}|")
        
        if msg.number in self.highlight:
            self.important_msgs.append(msg)

        if msg.filename is not None:
            print(msg)
            
            if msg.filename not in self.file_msgs and msg.level not in self.file_msgs[msg.filename]:
                print(f"File {msg.filename} has {msg.level.lower()}s...")

            if msg.number not in self.seen:
                print(f"New msg: {msg.major} {msg.minor} {msg.msg}")
                self.seen |= set([msg.number])
                
            self.file_msgs[msg.filename][msg.level][msg.line][msg.number].append(msg)
        else:
            print(msg)

        return True

    def show_locations(self):
        print("Message locations:")
        print(self.file_msgs.keys())
        
        for file, levels in self.file_msgs.items():
            for level, lines in levels.items():
                print(f"{file} has {len(lines)} with {level.lower()}s...")
