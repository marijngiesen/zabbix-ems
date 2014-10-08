import requests


class UrlCollector:
    url = None

    def __init__(self, url):
        self.url = url

    def get(self):
        return self._read()

    def _read(self):
        response = requests.get(self.url)
        return response