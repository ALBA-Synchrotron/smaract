# ------------------------------------------------------------------------------
# This file is part of smaract (https://github.com/ALBA-Synchrotron/smaract)
#
# Copyright 2008-2017 CELLS / ALBA Synchrotron, Bellaterra, Spain
#
# Distributed under the terms of the GNU General Public License,
# either version 3 of the License, or (at your option) any later version.
# See LICENSE.txt for more info.
#
# You should have received a copy of the GNU General Public License
# along with smaract. If not, see <http://www.gnu.org/licenses/>.
# ------------------------------------------------------------------------------


import unittest

from smaract import SmaractMCSController
from smaract.communication import *


class TestCommunication(unittest.TestCase):
    """
    This default values are required to execute the unittest from
    Pycharm. Edit when needed. These values can be easily overwritten when the
    tests are executed from the command line.
    """
    IP = '10.0.34.194'
    PORT = 5000
    TIMEOUT = 3

    def setUp(self):
        self.ctrl = SmaractMCSController(CommType.Socket, self.IP, self.PORT,
                                         self.TIMEOUT)

    def tearDown(self):
        self.ctrl._comm._comm.close()

    def test_connexion(self):
        print "\n*** Testing connection ***"
        try:
            print "Controller ID: %s" % self.ctrl.id
            print "Interface: %s" % self.ctrl.version
            print "Communication type: %s" % self.ctrl.comm_type
        except Exception as e:
            print '%s' % str(e)

        if isinstance(self.ctrl, SmaractMCSController):
            print "Communication mode: %s" % self.ctrl.communication_mode
            print "Number of channels: %s" % self.ctrl.nchannels

    def test_axes(self):
        print "\n*** Testing MCS axes ***"

        if isinstance(self.ctrl, SmaractMCSController):
            try:
                print "Axes/sensors enabled: %s" % self.ctrl.sensor_enabled

                for axis in self.ctrl:
                    self._axis_status(axis)

            except Exception as e:
                print '%s' % str(e)

    def _axis_status(self, a):
        print "Channel %s" % a._axis_nr
        print "\tState %s" % a.state
        print "\tStatus %s" % repr(a.status)
        print "\tSerial number: %s" % a.serial_number
        print "\tSensor type: %s" % a.sensor_type
        print "\tChannel type: %s" % a.channel_type
        print "\tFirmware version: %s" % repr(a.firmware_version)
        print "\tCurrent safe direction: %s" % a.safe_direction
        print "\tScale inverted: %s" % a.scale_inverted
        print "\tScale offset: %s" % a.scale_offset

    @ unittest.skip('RW properties test not fully implemented')
    def test_read_write(self):
        print "\n*** Testing MCS read/write properties ***"
        properties = ['closed_loop_vel', 'closed_loop_acc']
        self.ctrl.sensor_enabled = 1
        for axis in self.ctrl:
            for p in properties:
                print "\t R/W %s" % p
                v0 = getattr(axis, p)
                setattr(axis, p, v0 + 10)
                v1 = getattr(axis, p)
                self.assertEqual(v0 + 10, v1)


def parse_args():
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='controller', type=str)
    parser.add_argument('--port', help='port', type=str)
    parser.add_argument('--timeout', help='timeout', type=int)
    ns, args = parser.parse_known_args(namespace=unittest)
    print ns
    print args
    return ns, sys.argv[:1] + args


if __name__ == '__main__':
    ns, remaining_args = parse_args()
    TestCommunication.IP = ns.host
    TestCommunication.PORT = ns.port
    TestCommunication.TIMEOUT = ns.timeout
    unittest.main(verbosity=2, argv=remaining_args)
