from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from zems.lib.cache import Cache


class Redis(Check):
    name = "redis"
    db = None

    def _init_metrics(self):
        self.metrics = {
            "redis_version": Metric("redis_version", MetricType.String, 2, ":"),
            "uptime_in_seconds": Metric("uptime_in_seconds", MetricType.Integer, 14, ":"),
            "connected_clients": Metric("connected_clients", MetricType.Integer, 21, ":"),
            "client_longest_output_list": Metric("client_longest_output_list", MetricType.Integer, 22, ":"),
            "client_biggest_input_buf": Metric("client_biggest_input_buf", MetricType.Integer, 23, ":"),
            "blocked_clients": Metric("blocked_clients", MetricType.Integer, 24, ":"),
            "used_memory": Metric("used_memory", MetricType.Integer, 27, ":"),
            "used_memory_rss": Metric("used_memory_rss", MetricType.Integer, 29, ":"),
            "used_memory_peak": Metric("used_memory_peak", MetricType.Integer, 30, ":"),
            "used_memory_lua": Metric("used_memory_lua", MetricType.Integer, 32, ":"),
            "mem_fragmentation_ratio": Metric("mem_fragmentation_ratio", MetricType.Float, 33, ":"),
            "rdb_changes_since_last_save": Metric("rdb_changes_since_last_save", MetricType.Integer, 38, ":"),
            "rdb_last_save_time": Metric("rdb_last_save_time", MetricType.Integer, 40, ":"),
            "rdb_last_bgsave_status": Metric("rdb_last_bgsave_status", MetricType.String, 41, ":"),
            "rdb_last_bgsave_time_sec": Metric("rdb_last_bgsave_time_sec", MetricType.Integer, 42, ":"),
            "total_connections_received": Metric("total_connections_received", MetricType.Integer, 53, ":"),
            "total_commands_processed": Metric("total_commands_processed", MetricType.Integer, 54, ":"),
            "rejected_connections": Metric("rejected_connections", MetricType.Integer, 56, ":"),
            "expired_keys": Metric("expired_keys", MetricType.Integer, 60, ":"),
            "evicted_keys": Metric("evicted_keys", MetricType.Integer, 61, ":"),
            "keyspace_hits": Metric("keyspace_hits", MetricType.Integer, 62, ":"),
            "keyspace_misses": Metric("keyspace_misses", MetricType.Integer, 63, ":"),
            "connected_slaves": Metric("connected_slaves", MetricType.Integer, 70, ":"),
            "master_repl_offset": Metric("master_repl_offset", MetricType.Integer, 71, ":"),
            "used_cpu_sys": Metric("used_cpu_sys", MetricType.Float, 78, ":"),
            "used_cpu_user": Metric("used_cpu_user", MetricType.Float, 79, ":"),
            "used_cpu_sys_children": Metric("used_cpu_sys_children", MetricType.Float, 80, ":"),
            "used_cpu_user_children": Metric("used_cpu_user_children", MetricType.Float, 81, ":"),
            "keys": Metric("keys", MetricType.Integer, 0, "=", self._filter_data),
            "expires": Metric("expires", MetricType.Integer, 1, "=", self._filter_data),
            "avg_ttl": Metric("avg_ttl", MetricType.Integer, 2, "=", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.db = kwargs.get("db", None)

        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

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

