from serial import Serial
from socket import socket, AF_INET, SOCK_STREAM
import PyTango

# Define communication protocols
SERIAL_COM = 1
SERIAL_DS = 2
SOCKET_COM = 3


def _prepare_cmd(cmd):
    final_cmd = ':%s\n' % cmd
    return final_cmd


def _prepare_answer(raw_ans):
    ans = raw_ans[1:-1]
    return ans


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


class SerialCom(Serial):
    """
    Class which implements the Serial communication layer with ASCII interface
    for Smaract motion controllers.
    """
    @comm_error_handler
    def send_cmd(self, cmd):
        self.flush()
        data = _prepare_cmd(cmd)
        self.write(data)
        ans = _prepare_answer(self.readline())
        return ans


class SerialDSCom(object):
    """
    Class which implements the Serial (through TANGO DS Serial) communication
    layer with ASCii interface for Smaract motion controllers.
    """
    def __init__(self, ds_name):
        self.ds = PyTango.DeviceProxy(ds_name)

    @comm_error_handler
    def send_cmd(self, cmd):
        # flush both input and output
        self.ds.DevSerFlush(2)
        data = _prepare_cmd(cmd)
        self.ds.DevSerWriteString(data)
        ans = _prepare_answer(self.ds.DevSerReadLine())
        return ans


class SocketCom(socket):
    """
    Class which implements the Socket communication layer with ASCii interface
    for Smaract motion controllers.
    """
    def __init__(self, host='localhost', port=5000, timeout=3.0):
        super(SocketCom, self).__init__(family=AF_INET, type=SOCK_STREAM)
        self.connect((host, port))
        self.settimeout(timeout)

    @comm_error_handler
    def send_cmd(self, cmd):
        data = _prepare_cmd(cmd)
        self.sendall(data)
        ans = _prepare_answer(self.recv(1024))
        return ans


class ComBase(object):
    """
    Abstract class which provides a certain communication layer to the smaract
    motion controller.
    """
    def __init__(self, comm_type, *args):
        if comm_type == SERIAL_COM:
            self.com = SerialCom(*args)
        elif comm_type == SERIAL_DS:
            self.com = SerialDSCom(*args)
        elif comm_type == SOCKET_COM:
            self.com = SocketCom(*args)
        else:
            raise ValueError()

    def send_cmd(self, cmd):
        raise NotImplemented()
