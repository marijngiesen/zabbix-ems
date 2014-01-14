from zems.lib.socketcollector import *


class HAProxy:
    def __init__(self):
        pass

    @staticmethod
    def collect():
        parameters = SocketCollectorParameters()
        parameters.socketFile = "/var/lib/haproxy/stats.sock"

        collector = SocketCollector(parameters)
        return collector.get()
