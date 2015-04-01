from socket import *


class SocketConnector:
    family = None
    type = None
    socket_file = None
    host = None
    port = None
    command = None
    socket = None

    def __init__(self, socket_file=None, host=None, port=None,
                 command=None):
        if socket_file is not None:
            self.socket_file = socket_file
            self.family = AF_UNIX
        else:
            self.host = host
            self.port = int(port)
            self.family = AF_INET
        self.type = SOCK_STREAM
        self.command = command
        self.socket = socket(self.family, self.type)

    def get(self, command=None):
        self._connect()
        self._write(command)

        return self._read()

    def _connect(self):
        if self.socket_file is not None:
            self.socket.connect(self.socket_file)
        elif self.host is not None and self.port is not None:
            self.socket.connect((self.host, self.port))

    def _read(self):
        buf = ""
        while True:
            data = self.socket.recv(1024)
            buf += data
            if not data:
                self.socket.close()
                return buf

    def _write(self, command=None):
        if command is not None:
            self.command = command

        self.socket.send(self.command)
