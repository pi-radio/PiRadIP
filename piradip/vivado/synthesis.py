from .msghandler import VivadoMessageHandler
from collections import defaultdict, deque
import re

# 

class SynthesisMessageHandler(VivadoMessageHandler):
    unconnected_re = re.compile(r"Port (?P<port>\S+) in module (?P<module>\S+) is either unconnected or has no load")
    no_driver_re = re.compile(r"Net (?P<net>\S+) in module/entity (?P<module>\S+) does not have driver.")

    def unconnected(self, msg):
        m = self.unconnected_re.match(msg.msg)
        
        self.unconnected_ports[m["module"]].append(m["port"])

        msg.display = False

    def no_driver(self, msg):
        m = self.no_driver_re.match(msg.msg)
        
        self.no_driver_nets[m["module"]].append(m["net"])

        msg.display = False

        
    def ignore(level):
        def do_ignore(self, msg):
            msg.display = False
            msg.log = False
            pass
        return do_ignore

    def highlight(self, msg):
        self.important_msgs.append(msg)
        msg.style='#FFCCCC bold'
        
    def normal_msg(self, msg):
        pass
        
    def no_number_msg(self, msg):
        if msg.msg.startswith("synthesizing"):
            msg.display = False
            self.modules[msg.module]['file'] = msg.filename
            self.modules[msg.module]['line'] = msg.line
            self.modules[msg.module]['synthesizing'] = True
            print(f"Synthesizing {msg.module}...")
            return True
        elif msg.msg.startswith("done synthesizing"):
            msg.display = False
            print(f"Done with {msg.module}...")
            #assert self.modules[msg.module]['synthesizing'], f"{msg.module} marked as done {self.modules[msg.module]}"
            if not self.modules[msg.module]['synthesizing']:
                print(f"Never saw open for {msg.module}")
            self.modules[msg.module]['synthesizing'] = False
            return True
        elif msg.msg.find("synth") != -1:
            raise RuntimeError(f"NOT SYNTH: |{msg.msg}|")
        
    handlers = {
        None: no_number_msg,
        
        (8, 7129): unconnected,

        (8, 3848): no_driver,
        
        (8, 87): highlight, # Did *not* result in combanitorical logic
        (8, 327): highlight, # Inferred latch
        
        # Ignores
        (8, 113):  ignore(0),  # 'binding component instance'...
        (1, 1174): ignore(0),  # 'XPM XDC files'
        (8, 802):  ignore(0),  # Inferred FSM
        (8, 7079): ignore(0),  # Multithreading
        (8, 7078): ignore(0),  # Launching helper
        (8, 7075): ignore(0),  # Helper process
        (1, 236):  ignore(0),  # Implementation constriants
        
        # Maybe useful?
        (8, 226):  ignore(10),   # 'default block is never used'...
        (8, 7030): ignore(10),  # Implemented non-cascaded BRAM
        (8, 3332): ignore(10),  # Sequential element
        (8, 3333): ignore(10),  # Sequential element
        (8, 3295): ignore(10),  # Tying undriven pin
        (8, 5544): ignore(10),  # ROM too small for BRAM
        (8, 3491): ignore(10),  # bound to instance
        (8, 6014): ignore(10),  # Unused sequential
        (8, 5396): ignore(10),  # clock with keep attribute
        (8, 5578): ignore(10),  # Moved timing constraint
        (8, 7067): ignore(10),  # Removed DRAM instance
        (8, 6904): ignore(10),  # IMplemented with LUTRAM
        (8, 3886): ignore(10),  # merging instance
        (8, 3354): ignore(10),  # FSM encoding
        (8, 3971): ignore(10),  # TDP recognized

        (8, 3886): ignore(20),  # Merging instances
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

        self.unconnected_ports = defaultdict(list)
        self.no_driver_nets = defaultdict(list)
        
    def end_report(self):
        print("Highlighted messages:")
        for m in self.important_msgs:
            m.output()
        
    def handle_msg(self, msg):
        assert msg.facility == "Synth"

        if msg.msg.find("IBUF") != -1:
            print(f"IBUF: {msg}")

        handler = self.handlers.get(msg.number, SynthesisMessageHandler.normal_msg)

        handler(self, msg)

        if msg.level == 'INFO':
            msg.display = False
            
        if msg.filename is not None:
            if msg.number not in self.seen:
                self.seen |= set([msg.number])
                
            self.file_msgs[msg.filename][msg.level][msg.line][msg.number].append(msg)

        return True

    def show_locations(self):
        for file, levels in self.file_msgs.items():
            for level, lines in levels.items():
                if level == "INFO":
                    continue
                
                print(f"{file} has {len(lines)} lines with {level.lower()}s...")
                
                for line, msgs in lines.items():
                    for mno, msglist in msgs.items():
                        for msg in msglist:
                            msg.output()
                    
