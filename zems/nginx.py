from check import Check, CheckFail, MetricType, Metric
from lib.urlconnector import UrlConnector
from lib.cache import Cache


class Nginx(Check):
    name = "nginx"

    def _init_metrics(self):
        self.metrics = {
            "connections_active": Metric(MetricType.Integer, regex="Active connections: ([0-9]+)"),
            "connections_reading": Metric(MetricType.Integer, regex="Reading: ([0-9]+)"),
            "connections_writing": Metric(MetricType.Integer, regex="Writing: ([0-9]+)"),
            "connections_waiting": Metric(MetricType.Integer, regex="Waiting: ([0-9]+)"),
            "accepts": Metric(MetricType.Integer, linenumber=2, position=0, separator=" "),
            "handled": Metric(MetricType.Integer, linenumber=2, position=1, separator=" "),
            "requests": Metric(MetricType.Integer, linenumber=2, position=2, separator=" "),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        url = "%s://%s:%s%s" % (
            self.config.get("proto", "http"), self.config.get("host", "localhost"), self.config.get("port", "80"),
            self.config.get("resource", "/nginx-status")
        )

        connector = UrlConnector(url)
        data = connector.get()
        if data.status_code != 200:
            raise CheckFail("Unable to retrieve data (error code: %s)" % data.status_code)

        self.test_data = data.text.strip()
        Cache.write(self.name, self.test_data)