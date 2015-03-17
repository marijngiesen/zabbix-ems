from check import Check, MetricType, Metric
from lib.mysqlconnector import MySQLConnector
from lib.cache import Cache


class Sphinx(Check):
    name = "sphinx"

    def _init_metrics(self):
        self.metrics = {
            "uptime": Metric("uptime", MetricType.Integer, 0),
            "connections": Metric("connections", MetricType.Integer, 1),
            "maxed_out": Metric("maxed_out", MetricType.Integer, 2),
            "command_search": Metric("command_search", MetricType.Integer, 3),
            "command_excerpt": Metric("command_excerpt", MetricType.Integer, 4),
            "command_update": Metric("command_update", MetricType.Integer, 5),
            "command_keywords": Metric("command_keywords", MetricType.Integer, 6),
            "command_persist": Metric("command_persist", MetricType.Integer, 7),
            "command_status": Metric("command_status", MetricType.Integer, 8),
            "command_flushattrs": Metric("command_flushattrs", MetricType.Integer, 9),
            "agent_connect": Metric("agent_connect", MetricType.Integer, 10),
            "agent_retry": Metric("agent_retry", MetricType.Integer, 11),
            "queries": Metric("queries", MetricType.Integer, 12),
            "dist_queries": Metric("dist_queries", MetricType.Integer, 13),
            "query_wall": Metric("query_wall", MetricType.Float, 14),
            "query_cpu": Metric("query_cpu", MetricType.Float, 15),
            "dist_wall": Metric("dist_wall", MetricType.Float, 16),
            "dist_local": Metric("dist_local", MetricType.Float, 17),
            "dist_wait": Metric("dist_wait", MetricType.Float, 18),
            "query_reads": Metric("query_reads", MetricType.Float, 19),
            "query_readkb": Metric("query_readkb", MetricType.Float, 20),
            "query_readtime": Metric("query_readtime", MetricType.Float, 21),
            "avg_query_wall": Metric("avg_query_wall", MetricType.Float, 22),
            "avg_query_cpu": Metric("avg_query_cpu", MetricType.Float, 23),
            "avg_dist_wall": Metric("avg_dist_wall", MetricType.Float, 24),
            "avg_dist_local": Metric("avg_dist_local", MetricType.Float, 25),
            "avg_dist_wait": Metric("avg_dist_wait", MetricType.Float, 26),
            "avg_query_reads": Metric("avg_query_reads", MetricType.Float, 27),
            "avg_query_readkb": Metric("avg_query_readkb", MetricType.Float, 28),
            "avg_query_readtime": Metric("avg_query_readtime", MetricType.Float, 29),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if self.test_data[metric.key] == "OFF" and not metric.type == MetricType.String:
            self.test_data[metric.key] = ""

        return self._correct_type(metric.type, self.test_data[metric.key])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self._format_data(self.test_data)

        connector = MySQLConnector(host=self.config.get("host", "127.0.0.1"), port=self.config.get("port", 9306))
        data = connector.get("SHOW STATUS")
        Cache.write(self.name, data)

        return self._format_data(data)

    def _format_data(self, data):
        tmp = {}
        for value in data:
            tmp[value["Counter"]] = value["Value"]

        return tmp

    def _filter_data(self, linenumber, separator, key):
        data = self.test_data[linenumber].split(separator)[1].count(key)
        self.test_data[linenumber] = str(key) + ":" + str(data)

