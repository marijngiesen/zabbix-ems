from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from zems.lib.cache import Cache


class Redis(Check):
    name = "redis"
    db = None

    def _init_metrics(self):
        self.metrics = {
            "redis_version": Metric("redis_version", 2, MetricType.String, ":"),
            "uptime_in_seconds": Metric("uptime_in_seconds", 14, MetricType.Integer, ":"),
            "connected_clients": Metric("connected_clients", 21, MetricType.Integer, ":"),
            "client_longest_output_list": Metric("client_longest_output_list", 22, MetricType.Integer, ":"),
            "client_biggest_input_buf": Metric("client_biggest_input_buf", 23, MetricType.Integer, ":"),
            "blocked_clients": Metric("blocked_clients", 24, MetricType.Integer, ":"),
            "used_memory": Metric("used_memory", 27, MetricType.Integer, ":"),
            "used_memory_rss": Metric("used_memory_rss", 29, MetricType.Integer, ":"),
            "used_memory_peak": Metric("used_memory_peak", 30, MetricType.Integer, ":"),
            "used_memory_lua": Metric("used_memory_lua", 32, MetricType.Integer, ":"),
            "mem_fragmentation_ratio": Metric("mem_fragmentation_ratio", 33, MetricType.Float, ":"),
            "rdb_changes_since_last_save": Metric("rdb_changes_since_last_save", 38, MetricType.Integer, ":"),
            "rdb_last_save_time": Metric("rdb_last_save_time", 40, MetricType.Integer, ":"),
            "rdb_last_bgsave_status": Metric("rdb_last_bgsave_status", 41, MetricType.String, ":"),
            "rdb_last_bgsave_time_sec": Metric("rdb_last_bgsave_time_sec", 42, MetricType.Integer, ":"),
            "total_connections_received": Metric("total_connections_received", 53, MetricType.Integer, ":"),
            "total_commands_processed": Metric("total_commands_processed", 54, MetricType.Integer, ":"),
            "rejected_connections": Metric("rejected_connections", 56, MetricType.Integer, ":"),
            "expired_keys": Metric("expired_keys", 60, MetricType.Integer, ":"),
            "evicted_keys": Metric("evicted_keys", 61, MetricType.Integer, ":"),
            "keyspace_hits": Metric("keyspace_hits", 62, MetricType.Integer, ":"),
            "keyspace_misses": Metric("keyspace_misses", 63, MetricType.Integer, ":"),
            "connected_slaves": Metric("connected_slaves", 70, MetricType.Integer, ":"),
            "master_repl_offset": Metric("master_repl_offset", 71, MetricType.Integer, ":"),
            "used_cpu_sys": Metric("used_cpu_sys", 78, MetricType.Float, ":"),
            "used_cpu_user": Metric("used_cpu_user", 79, MetricType.Float, ":"),
            "used_cpu_sys_children": Metric("used_cpu_sys_children", 80, MetricType.Float, ":"),
            "used_cpu_user_children": Metric("used_cpu_user_children", 81, MetricType.Float, ":"),
            "keys": Metric("keys", 0, MetricType.Integer, "=", self._filter_data),
            "expires": Metric("expires", 1, MetricType.Integer, "=", self._filter_data),
            "avg_ttl": Metric("avg_ttl", 2, MetricType.Integer, "=", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.db = kwargs.get("db", None)

        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        if metric.filter_callback is not None:
            metric.filter_callback(":")

        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        connector = SocketConnector(host=self.config.get("host", "localhost"),
                                    port=self.config.get("port", "6379"),
                                    command="info\r\nquit\r\n")

        data = connector.get().strip("\r")
        Cache.write(self.name, data)

        return data.split("\n")

    def _filter_data(self, separator):
        if self.db is None:
            raise CheckFail("Required parameters not set (db)")

        for db_id, line in enumerate(self.test_data):
            values = line.split(separator)

            if self.db in values:
                self.test_data = values[1].split(",")

