from check import Check, CheckFail, MetricType, Metric
from lib.mysqlconnector import MySQLConnector
from lib.cache import Cache


class Sphinx(Check):
    name = "sphinx"

    def _init_metrics(self):
        self.metrics = {
            "uptime": Metric("uptime", 0, MetricType.Integer),
            "connections": Metric("connections", 1, MetricType.Integer),
            "maxed_out": Metric("maxed_out", 2, MetricType.Integer),
            "command_search": Metric("command_search", 3, MetricType.Integer),
            "command_excerpt": Metric("command_excerpt", 4, MetricType.Integer),
            "command_update": Metric("command_update", 5, MetricType.Integer),
            "command_keywords": Metric("command_keywords", 6, MetricType.Integer),
            "command_persist": Metric("command_persist", 7, MetricType.Integer),
            "command_status": Metric("command_status", 8, MetricType.Integer),
            "command_flushattrs": Metric("command_flushattrs", 9, MetricType.Integer),
            "agent_connect": Metric("agent_connect", 10, MetricType.Integer),
            "agent_retry": Metric("agent_retry", 11, MetricType.Integer),
            "queries": Metric("queries", 12, MetricType.Integer),
            "dist_queries": Metric("dist_queries", 13, MetricType.Integer),
            "query_wall": Metric("query_wall", 14, MetricType.Float),
            "query_cpu": Metric("query_cpu", 15, MetricType.Float),
            "dist_wall": Metric("dist_wall", 16, MetricType.Float),
            "dist_local": Metric("dist_local", 17, MetricType.Float),
            "dist_wait": Metric("dist_wait", 18, MetricType.Float),
            "query_reads": Metric("query_reads", 19, MetricType.Float),
            "query_readkb": Metric("query_readkb", 20, MetricType.Float),
            "query_readtime": Metric("query_readtime", 21, MetricType.Float),
            "avg_query_wall": Metric("avg_query_wall", 22, MetricType.Float),
            "avg_query_cpu": Metric("avg_query_cpu", 23, MetricType.Float),
            "avg_dist_wall": Metric("avg_dist_wall", 24, MetricType.Float),
            "avg_dist_local": Metric("avg_dist_local", 25, MetricType.Float),
            "avg_dist_wait": Metric("avg_dist_wait", 26, MetricType.Float),
            "avg_query_reads": Metric("avg_query_reads", 27, MetricType.Float),
            "avg_query_readkb": Metric("avg_query_readkb", 28, MetricType.Float),
            "avg_query_readtime": Metric("avg_query_readtime", 29, MetricType.Float),
        }

    def _get(self, metric=None, *args, **kwargs):
        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        if self.test_data[metric.key] == "OFF" and not metric.type == MetricType.String:
            self.test_data[metric.key] = ""

        return self._correct_type(metric.type, self.test_data[metric.key])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        connector = MySQLConnector(host=self.config.get("host", "127.0.0.1"), port=self.config.get("port", 9306))
        data = connector.get("SHOW STATUS")

        tmp = {}
        for value in data:
            tmp[value["Counter"]] = value["Value"]

        # Cache.write(self.name, data)
        return tmp

    def _filter_data(self, linenumber, separator, key):
        data = self.test_data[linenumber].split(separator)[1].count(key)
        self.test_data[linenumber] = str(key) + ":" + str(data)

