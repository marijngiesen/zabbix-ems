try:
    import requests
except ImportError:
    import sys
    requests = None
    print "Error: requests module cannot be loaded, please install using 'pip install requests'"
    sys.exit(1)


class UrlConnector:
    url = None
    load_time = 0
    load_time_regex = "Load_time: ([0-9\.]+)"

    def __init__(self, url):
        self.url = url

    def get(self):
        response = self._read()
        self.load_time = '%d.%06d' % (response.elapsed.seconds, response.elapsed.microseconds)

        return response

    def get_load_time(self):
        return "\nLoad_time: %s" % str(self.load_time)

    def _read(self):
        return requests.get(self.url)
