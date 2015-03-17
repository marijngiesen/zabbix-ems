from check import Check, CheckFail, MetricType, Metric
from lib.urlconnector import UrlConnector
from lib.cache import Cache


class Apache(Check):
    name = "apache"

    def _init_metrics(self):
        self.metrics = {
            "workers_busy": Metric("BusyWorkers", MetricType.Integer, 0, ":"),
            "workers_idle": Metric("IdleWorkers", MetricType.Integer, 1, ":"),
            "workers_closing": Metric("C", MetricType.Integer, 2, ":", self._filter_data),
            "workers_dns": Metric("D", MetricType.Integer, 2, ":", self._filter_data),
            "workers_finishing": Metric("G", MetricType.Integer, 2, ":", self._filter_data),
            "workers_idlecleanup": Metric("I", MetricType.Integer, 2, ":", self._filter_data),
            "workers_keepalive": Metric("K", MetricType.Integer, 2, ":", self._filter_data),
            "workers_logging": Metric("L", MetricType.Integer, 2, ":", self._filter_data),
            "workers_openslot": Metric(".", MetricType.Integer, 2, ":", self._filter_data),
            "workers_reading": Metric("R", MetricType.Integer, 2, ":", self._filter_data),
            "workers_starting": Metric("S", MetricType.Integer, 2, ":", self._filter_data),
            "workers_writing": Metric("W", MetricType.Integer, 2, ":", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

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
