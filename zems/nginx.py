from commandr import command
from check import Check, CheckFail, MetricType, Metric
from lib.urlcollector import UrlCollector
from lib.cache import Cache


class Nginx(Check):
    name = "nginx"

    def _init_metrics(self):
        self.metrics = {
            "connections_active": Metric("active connections", 0, MetricType.Integer, ":"),
            "connections_reading": Metric("reading", 1, MetricType.Integer, " ", self._filter_data, linenumber=3),
            "connections_writing": Metric("writing", 3, MetricType.Integer, " ", self._filter_data, linenumber=3),
            "connections_waiting": Metric("waiting", 5, MetricType.Integer, " ", self._filter_data, linenumber=3),
            "accepts": Metric("accepts", 0, MetricType.Integer, " ", self._filter_data, linenumber=2),
            "handled": Metric("handled", 1, MetricType.Integer, " ", self._filter_data, linenumber=2),
            "requests": Metric("requests", 2, MetricType.Integer, " ", self._filter_data, linenumber=2),
        }

    def _get(self, metric=None, *args, **kwargs):
        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

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

        collector = UrlCollector(url)
        data = collector.get()
        if data.status_code != 200:
            raise CheckFail("Unable to retrieve data (error code: %s)" % data.status_code)

        data = data.text.strip()
        Cache.write(self.name, data)

        return data.split("\n")

    def _filter_data(self, linenumber, separator):
        self.test_data = self.test_data[linenumber].strip().split(separator)


@command("nginx")
def nginx(key=None):
    test = Nginx()

    if key is not None:
        test.get(key)
    else:
        test.print_metrics()
