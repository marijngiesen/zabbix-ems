from zems.lib.cache import *
from socket import *


class SocketCollector:
    socket = None
    parameters = None

    def __init__(self, parameters):
        self.parameters = parameters
        self.socket = socket(parameters.family, parameters.type)

    def get(self):
        self._connect()
        self._write()
        return self._read()

    def _connect(self):
        print "Connect to: %s" % self.parameters.socketFile
        self.socket.connect(self.parameters.socketFile)

    def _read(self):
        buffer = ""
        print "Received data:"
        while True:
            data = self.socket.recv(1024)
            buffer += data
            if not data:
                self.socket.close()
                return buffer

    def _write(self):
        print "Send command: %s" % self.parameters.command
        self.socket.send(self.parameters.command)


class SocketCollectorParameters:
    useCache = True
    family = AF_UNIX
    type = SOCK_STREAM
    socketFile = None
    host = None
    port = None
    command = None

    def __init__(self):
        pass

