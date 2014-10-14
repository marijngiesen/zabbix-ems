from check import Check, CheckFail, MetricType, Metric
from lib.urlconnector import UrlConnector
from lib.cache import Cache


class Apache(Check):
    name = "apache"

    def _init_metrics(self):
        self.metrics = {
            "workers_busy": Metric("BusyWorkers", 0, MetricType.Integer, ":"),
            "workers_idle": Metric("IdleWorkers", 1, MetricType.Integer, ":"),
            "workers_closing": Metric("C", 2, MetricType.Integer, ":", self._filter_data),
            "workers_dns": Metric("D", 2, MetricType.Integer, ":", self._filter_data),
            "workers_finishing": Metric("G", 2, MetricType.Integer, ":", self._filter_data),
            "workers_idlecleanup": Metric("I", 2, MetricType.Integer, ":", self._filter_data),
            "workers_keepalive": Metric("K", 2, MetricType.Integer, ":", self._filter_data),
            "workers_logging": Metric("L", 2, MetricType.Integer, ":", self._filter_data),
            "workers_openslot": Metric(".", 2, MetricType.Integer, ":", self._filter_data),
            "workers_reading": Metric("R", 2, MetricType.Integer, ":", self._filter_data),
            "workers_starting": Metric("S", 2, MetricType.Integer, ":", self._filter_data),
            "workers_writing": Metric("W", 2, MetricType.Integer, ":", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        if metric.filter_callback is not None:
            metric.filter_callback(metric.position, metric.separator, metric.key)

        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        url = "%s://%s:%s%s?auto" % (
            self.config.get("proto", "http"), self.config.get("host", "localhost"), self.config.get("port", "80"),
            self.config.get("resource", "/server-status")
        )

        connector = UrlConnector(url)
        data = connector.get()
        if data.status_code != 200:
            raise CheckFail("Unable to retrieve data (error code: %s)" % data.status_code)

        data = data.text.strip()
        Cache.write(self.name, data)

        return data.split("\n")

    def _filter_data(self, linenumber, separator, key):
        data = self.test_data[linenumber].split(separator)[1].count(key)
        self.test_data[linenumber] = str(key) + ":" + str(data)
