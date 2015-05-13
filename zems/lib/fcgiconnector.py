from time import time
import flup_fcgi_client as fcgi_client


class FcgiConnector:
    socket_file = None
    host = None
    port = None
    uri = None
    load_time = 0
    load_time_regex = "Load_time: ([0-9\.]+)"

    def __init__(self, socket_file=None, host=None, port=None,
                 uri=None):
        self.socket_file = socket_file
        self.host = host
        self.port = int(port)
        self.uri = uri

    def get(self):
        return self._read()

    def _read(self):
        start_time = time()
        if self.socket_file is not None:
            fcgi = fcgi_client.FCGIApp(connect=self.socket_file)
        elif self.host is not None and self.port is not None:
            fcgi = fcgi_client.FCGIApp(host=self.host, port=self.port)
        else:
            raise Exception("No socket_file, host or port given as parameter")

        if self.uri is None:
            raise Exception("No valid URI given")

        env = {
            'SCRIPT_FILENAME': self.uri,
            'QUERY_STRING': '',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': self.uri,
            'REQUEST_URI': self.uri,
            'GATEWAY_INTERFACE': 'CGI/1.1',
            'SERVER_SOFTWARE': 'zems',
            'REDIRECT_STATUS': '200',
            'CONTENT_TYPE': '',
            'CONTENT_LENGTH': '0',
            # 'DOCUMENT_URI': url,
            'DOCUMENT_ROOT': '/var/www/'
        }

        result = fcgi(env)
        self.load_time = time() - start_time

        return result

    def get_load_time(self):
        return "Load_time: %s" % str(self.load_time)
