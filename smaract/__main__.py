#!/usr/bin/env python
print "hello"
from constants import *
from controller import *
from axis import *
from communication import *


#mcs = SmaractMCSController(CommType.Socket,'10.0.34.194')
mcs = SmaractMCSController(CommType.Socket,'10.0.34.194', 5000, 3)
print "Gathering system information...\n"
print "Controller ID: %s" % mcs.id
print "Interface: %s" % mcs.version
print "Number of channels: %s" % mcs.nchannels 
print "Communication mode: %s" % mcs.communication_mode
print ""


for a in mcs:
    print "Channel %s" % mcs[0]._axis_nr
    print "\tState %s" % a.status
    print "\tSensor type: %s" % a.sensor_type
    print "\tCurrent safe direction: %s" % a.safe_direction
    
    f_mcs = True
    if f_mcs:
        print "\tChannel type: %s" % a.channel_type