from twisted.internet import reactor
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet.protocol import Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint, connectProtocol

import socket
import json

EOS=-1
EOM=-2

class TCFProtocol(Protocol):
    def __init__(self):
        super().__init__()
        self.buf = b''
        self.seq=0
        self._tokens = []
        
        
    def dataReceived(self, data):
        self.buf += data

        self.parse_data()

    def eventReceived(self, service, event, data):
        print(f"EVENT: {service} {event} {data}")

        data = json.loads(data)

    def messageReceived(self, m):
        if m[0] == 'E':
            self.eventReceived(*m[1:])
        elif m[0] == 'C':
            self.commandReceived(*m[1:])
        elif m[0] == 'R':
            self.resultReceived(*m[1:])
        elif m[0] == 'F':
            self.flowControl(*m[1:])
        else:
            raise RuntimeError("Unknown message type")
        
    def parse_data(self):
        while len(self.buf):
            i = 0

            if self.buf[i] == 1:
                self.buf = self.buf[1:]
                print("End of message")
                m = tuple(map(lambda x: x.decode(), self._tokens))
                self._tokens = []
                self.messageReceived(m)
                pass
            elif self.buf[i] == 2:
                pass
            elif self.buf[i] == 3:
                print("Bizarre code...")
                self.buf = self.buf[1:]
                continue
            
            while i < len(self.buf) and self.buf[i] != 0:
                i += 1

            if i == len(self.buf):
                break

            # Advance the parser
            s = self.buf[:i]
            delim = self.buf[i]
            self.buf = self.buf[i+1:]

            self._tokens.append(s)
            
            print(s)
        
    def lineReceived(self, data):
        print(data)

        
def gotProtocol(p):
    print("gotProtocol")
        
ep = TCP4ClientEndpoint(reactor, "10.77.200.27", 3121)

d = connectProtocol(ep, TCFProtocol())
d.addCallback(gotProtocol)
reactor.run()
