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


from serial import Serial
from socket import socket, AF_INET, SOCK_STREAM


def comm_error_handler(f):
    """
    Error handling function (decorator).
    @param f: target function.
    @return: decorated function with error handling.
    """
    def new_func(*args, **kwargs):
        try:
            ans = f(*args, **kwargs)
            return ans
        except Exception, e:
            msg = ('Problem with the communication. Verify the hardware. '
                   'Error: %s' % e)
            raise RuntimeError(msg)
    return new_func


class CommType(object):
    Serial = 1
    SerialTango = 2
    Socket = 3


class SmaractCommunication(object):
    """
    Abstract class which provides a certain communication layer to the smaract
    motion controller.
    """
    def __init__(self, comm_type, *args):
        if comm_type == CommType.Serial:
            self._comm = SerialCom(*args)
            self._comm_type = CommType.Serial
        elif comm_type == CommType.SerialTango:
            self._comm = SerialTangoCom(*args)
            self._comm_type = CommType.SerialTango
        elif comm_type == CommType.Socket:
            self._comm = SocketCom(*args)
            self._comm_type = CommType.Socket
        else:
            raise ValueError()

    def send_cmd(self, cmd):
        cmd = ':%s\n' % cmd
        ans = self._comm.send_cmd(cmd)
        return ans[1:-1]

    def get_comm_type(self):
        return self._comm_type


class SerialCom(Serial):
    """
    Class which implements the Serial communication layer with ASCII interface
    for Smaract motion controllers.
    """
    @comm_error_handler
    def send_cmd(self, cmd):
        self.flush()
        self.write(cmd)
        return self.readline()


class SerialTangoCom(object):
    """
    Class which implements the Serial (through TANGO Device Serial)
    communication layer with ASCii interface for Smaract motion controllers.
    """
    def __init__(self, device_name):
        import PyTango
        self.device = PyTango.DeviceProxy(device_name)

    @comm_error_handler
    def send_cmd(self, cmd):
        # flush both input and output
        self.device.DevSerFlush(2)
        self.device.DevSerWriteString(cmd)
        return self.device.DevSerReadLine()


class SocketCom(socket):
    """
    Class which implements the Socket communication layer with ASCii interface
    for Smaract motion controllers.
    """
    def __init__(self, host='localhost', port=5000, timeout=3.0):
        super(SocketCom, self).__init__(family=AF_INET, type=SOCK_STREAM)
        self.settimeout(timeout)
        try:
            self.connect((host, port))
        except Exception as e:
            raise RuntimeError('There are problem to connect to the smaract. '
                               'Maybe there is another client connected. '
                               'Error: %s' % e)
    @comm_error_handler
    def send_cmd(self, cmd):
        self.sendall(cmd)
        return self.recv(1024)
