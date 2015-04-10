from check import Check, CheckFail, MetricType, Metric
from lib.urlconnector import UrlConnector
from lib.cache import Cache


class Apache(Check):
    name = "apache"

    def _init_metrics(self):
        self.metrics = {
            "total_accesses": Metric(MetricType.Integer, regex="Total Accesses: ([0-9]+)"),
            "total_traffic": Metric(MetricType.Integer, regex="Total kBytes: ([0-9]+)"),
            "cpuload": Metric(MetricType.Float, regex="CPULoad: ([0-9\.]+)"),
            "uptime": Metric(MetricType.Integer, regex="Uptime: ([0-9]+)"),
            "req_per_sec": Metric(MetricType.Float, regex="ReqPerSec: ([0-9\.]+)"),
            "bytes_per_sec": Metric(MetricType.Float, regex="BytesPerSec: ([0-9\.]+)"),
            "bytes_per_req": Metric(MetricType.Float, regex="BytesPerReq: ([0-9\.]+)"),
            "workers_busy": Metric(MetricType.Integer, regex="BusyWorkers: ([0-9]+)"),
            "workers_idle": Metric(MetricType.Integer, regex="IdleWorkers: ([0-9]+)"),
            "workers_closing": Metric(MetricType.Integer, self._parse_scoreboard, key="C"),
            "workers_dns": Metric(MetricType.Integer, self._parse_scoreboard, key="D"),
            "workers_finishing": Metric(MetricType.Integer, self._parse_scoreboard, key="G"),
            "workers_idlecleanup": Metric(MetricType.Integer, self._parse_scoreboard, key="I"),
            "workers_keepalive": Metric(MetricType.Integer, self._parse_scoreboard, key="K"),
            "workers_logging": Metric(MetricType.Integer, self._parse_scoreboard, key="L"),
            "workers_openslot": Metric(MetricType.Integer, self._parse_scoreboard, key="."),
            "workers_reading": Metric(MetricType.Integer, self._parse_scoreboard, key="R"),
            "workers_starting": Metric(MetricType.Integer, self._parse_scoreboard, key="S"),
            "workers_writing": Metric(MetricType.Integer, self._parse_scoreboard, key="W"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.callback is not None:
            metric.callback(metric.kwargs.get("key"))

        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        url = "%s://%s:%s%s?auto" % (
            self.config.get("proto", "http"), self.config.get("host", "localhost"), self.config.get("port", "80"),
            self.config.get("resource", "/server-status")
        )

        connector = UrlConnector(url)
        data = connector.get()
        if data.status_code != 200:
            raise CheckFail("Unable to retrieve data (error code: %s)" % data.status_code)

        self.test_data = data.text.strip()
        Cache.write(self.name, self.test_data)

    def _parse_scoreboard(self, key):
        position = self.test_data.index("Scoreboard:")
        line = self.test_data[position:].split("\n")[0]
        self.test_data = line.count(key)
