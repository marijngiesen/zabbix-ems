from check import Check, CheckFail, MetricType, Metric
from lib.urlconnector import UrlConnector
from lib.cache import Cache


class Nginx(Check):
    name = "nginx"

    def _init_metrics(self):
        self.metrics = {
            "connections_active": Metric("active connections", MetricType.Integer, 0, ":"),
            "connections_reading": Metric("reading", MetricType.Integer, 1, " ", self._filter_data),
            "connections_writing": Metric("writing", MetricType.Integer, 3, " ", self._filter_data),
            "connections_waiting": Metric("waiting", MetricType.Integer, 5, " ", self._filter_data),
            "accepts": Metric("accepts", MetricType.Integer, 0, " ", self._filter_data),
            "handled": Metric("handled", MetricType.Integer, 1, " ", self._filter_data),
            "requests": Metric("requests", MetricType.Integer, 2, " ", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.filter_callback is not None:
            metric.filter_callback(metric.kwargs.get("linenumber"), metric.separator)
            return self._correct_type(metric.type, self.test_data[metric.position])

        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        url = "%s://%s:%s%s" % (
            self.config.get("proto", "http"), self.config.get("host", "localhost"), self.config.get("port", "80"),
            self.config.get("resource", "/nginx-status")
        )

        connector = UrlConnector(url)
        data = connector.get()
        if data.status_code != 200:
            raise CheckFail("Unable to retrieve data (error code: %s)" % data.status_code)

        data = data.text.strip()
        Cache.write(self.name, data)

        return data.split("\n")

    def _filter_data(self, linenumber, separator):
        self.test_data = self.test_data[linenumber].strip().split(separator)


