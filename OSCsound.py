# OSCsound - Version 0.1
# Author: Steven Yi
#
# Script for rapid live Csound application development with OSC
# 
# Licensed under LGPL. Please view LICENSE for more information.
#

from csnd6 import Csound, CsoundPerformanceThread, csoundInitialize
from OSC import OSCServer
from time import sleep
import argparse
import types

# setup csound
csoundInitialize(3)
csound = None
csPerfThread = None

def csound_start(csd_file):
    global csound 
    global csPerfThread

    csound = Csound()
    csound.SetOption("-odac")  
    csound.Compile(csd_file)     
    csound.Start()  
    csPerfThread = CsoundPerformanceThread(csound)
    csPerfThread.Play()

def csound_stop():
    global csPerfThread
    global csound
    csPerfThread.Stop()
    csPerfThread.Join()
    csound.Stop()

###

server = None
run = True

def handle_timeout(self):
    self.timed_out = True

def handle_score(path, tags, args, source):
    global csPerfThread
    #print "TESTING", args[0]
    csPerfThread.InputMessage(args[0])

def handle_cc(path, tags, args, source):
    global csound
    if(len(args) != 2):
        print "Error: CC must have two args: channelName floatValue"
        return
    #print "TESTING: %s %s"%(args[0], args[1])
    csound.SetChannel(args[0], args[1])

def quit_callback(path, tags, args, source):
    global run
    run = False
    print "Quitting Server..."


def each_frame():
    global server
    server.timed_out = False
    while not server.timed_out:
        server.handle_request()


def server_start(port=7110):
    global server
    server = OSCServer ( ("localhost", 7110))
    server.timeout = 0

    server.handle_timeout = types.MethodType(handle_timeout, server)

    server.addMsgHandler("/sco", handle_score)
    server.addMsgHandler("/cc", handle_cc)
    server.addMsgHandler("/quit", quit_callback)

def server_stop():
    global server 
    server.close()




def main():
    
    parser = argparse.ArgumentParser(prog='OSCsound', 
                                     description='OSCsound - version 0.1')

    parser.add_argument("csd_file", help="Csound CSD File to run")
    parser.add_argument("-p", "--port", help="Server Port, defaults to 7110", type=int, default=7110)

    args = parser.parse_args()

    csound_start(args.csd_file)
    server_start(args.port)

    while run:
        sleep(1)
        each_frame()

    csound_stop()
    server_stop()

if __name__ == '__main__':
    main()
