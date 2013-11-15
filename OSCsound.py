from csnd6 import Csound, CsoundPerformanceThread, csoundInitialize
from OSC import OSCServer
from time import sleep

# setup csound
csoundInitialize(1)
orc = """
sr=44100
ksmps=32
nchnls=2
0dbfs=1

instr 1 
aout vco2 0.5, 440
outs aout, aout
endin"""


# Defining our Csound SCO code 
sco = "i1 0 1"

cs = Csound()
cs.SetOption("-odac")  # Using SetOption() to configure Csound
                      # Note: use only one commandline flag at a time

cs.CompileOrc(orc)     # Compile the Csound Orchestra string
#cs.ReadScore(sco)      # Compile the Csound SCO String
cs.Start()  # When compiling from strings, this call is necessary before doing any performing
pt = CsoundPerformanceThread(cs)
pt.Play()

###

server = OSCServer ( ("localhost", 7110))
server.timeout = 0
run = True


def handle_timeout(self):
    self.timed_out = True

import types
server.handle_timeout = types.MethodType(handle_timeout, server)


def handle_score(path, tags, args, source):
    #print "TESTING", args[0]
    pt.InputMessage(args[0])

def handle_cc(path, tags, args, source):
    if(len(args) != 2):
        print "Error: CC must have two args: channelName floatValue"
        return
    #print "TESTING: %s %s"%(args[0], args[1])
    cs.SetChannel(args[0], args[1])

def quit_callback(path, tags, args, source):
    global run
    run = False
    print "Quitting Server..."

server.addMsgHandler("/sco", handle_score)
server.addMsgHandler("/cc", handle_cc)
server.addMsgHandler("/quit", quit_callback)

def each_frame():
    server.timed_out = False
    while not server.timed_out:
        server.handle_request()

print "Starting OSC Server..."
while run:
    sleep(1)
    each_frame()

server.close()
pt.Stop()
pt.Join()
cs.Stop()


