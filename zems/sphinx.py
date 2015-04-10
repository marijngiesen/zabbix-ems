from check import Check, MetricType, Metric
from lib.mysqlconnector import MySQLConnector
from lib.cache import Cache


class Sphinx(Check):
    name = "sphinx"

    def _init_metrics(self):
        self.metrics = {
            "uptime": Metric(MetricType.Integer, key="uptime"),
            "connections": Metric(MetricType.Integer, key="connections"),
            "maxed_out": Metric(MetricType.Integer, key="maxed_out"),
            "command_search": Metric(MetricType.Integer, key="command_search"),
            "command_excerpt": Metric(MetricType.Integer, key="command_excerpt"),
            "command_update": Metric(MetricType.Integer, key="command_update"),
            "command_keywords": Metric(MetricType.Integer, key="command_keywords"),
            "command_persist": Metric(MetricType.Integer, key="command_persist"),
            "command_status": Metric(MetricType.Integer, key="command_status"),
            "command_flushattrs": Metric(MetricType.Integer, key="command_flushattrs"),
            "agent_connect": Metric(MetricType.Integer, key="agent_connect"),
            "agent_retry": Metric(MetricType.Integer, key="agent_retry"),
            "queries": Metric(MetricType.Integer, key="queries"),
            "dist_queries": Metric(MetricType.Integer, key="dist_queries"),
            "query_wall": Metric(MetricType.Float, key="query_wall"),
            "query_cpu": Metric(MetricType.Float, key="query_cpu"),
            "dist_wall": Metric(MetricType.Float, key="dist_wall"),
            "dist_local": Metric(MetricType.Float, key="dist_local"),
            "dist_wait": Metric(MetricType.Float, key="dist_wait"),
            "query_reads": Metric(MetricType.Float, key="query_reads"),
            "query_readkb": Metric(MetricType.Float, key="query_readkb"),
            "query_readtime": Metric(MetricType.Float, key="query_readtime"),
            "avg_query_wall": Metric(MetricType.Float, key="avg_query_wall"),
            "avg_query_cpu": Metric(MetricType.Float, key="avg_query_cpu"),
            "avg_dist_wall": Metric(MetricType.Float, key="avg_dist_wall"),
            "avg_dist_local": Metric(MetricType.Float, key="avg_dist_local"),
            "avg_dist_wait": Metric(MetricType.Float, key="avg_dist_wait"),
            "avg_query_reads": Metric(MetricType.Float, key="avg_query_reads"),
            "avg_query_readkb": Metric(MetricType.Float, key="avg_query_readkb"),
            "avg_query_readtime": Metric(MetricType.Float, key="avg_query_readtime"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        key = metric.kwargs.get("key")
        if self.test_data[key] == "OFF" and not metric.type == MetricType.String:
            self.test_data[key] = ""

        return self._correct_type(metric.type, self.test_data[key])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        connector = MySQLConnector(host=self.config.get("host", "127.0.0.1"), port=self.config.get("port", 9306))
        self.test_data = self._format_data(connector.get("SHOW STATUS"))

        Cache.write(self.name, self.test_data)

    def _format_data(self, data):
        tmp = {}
        for value in data:
            tmp[value["Counter"]] = value["Value"]

        return tmp

