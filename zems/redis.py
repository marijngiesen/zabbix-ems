from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from zems.lib.cache import Cache


class Redis(Check):
    name = "redis"
    db = None

    def _init_metrics(self):
        self.metrics = {
            "redis_version": Metric(MetricType.String, regex="redis_version:(.+)"),
            "uptime_in_seconds": Metric(MetricType.Integer, regex="uptime_in_seconds:([0-9]+)"),
            "connected_clients": Metric(MetricType.Integer, regex="connected_clients:([0-9]+)"),
            "client_longest_output_list": Metric(MetricType.Integer, regex="client_longest_output_list:([0-9]+)"),
            "client_biggest_input_buf": Metric(MetricType.Integer, regex="client_biggest_input_buf:([0-9]+)"),
            "blocked_clients": Metric(MetricType.Integer, regex="blocked_clients:([0-9]+)"),
            "used_memory": Metric(MetricType.Integer, regex="used_memory:([0-9]+)"),
            "used_memory_rss": Metric(MetricType.Integer, regex="used_memory_rss:([0-9]+)"),
            "used_memory_peak": Metric(MetricType.Integer, regex="used_memory_peak:([0-9]+)"),
            "used_memory_lua": Metric(MetricType.Integer, regex="used_memory_lua:([0-9]+)"),
            "mem_fragmentation_ratio": Metric(MetricType.Float, regex="mem_fragmentation_ratio:([0-9\.]+)"),
            "rdb_changes_since_last_save": Metric(MetricType.Integer, regex="rdb_changes_since_last_save:([0-9]+)"),
            "rdb_last_save_time": Metric(MetricType.Integer, regex="rdb_last_save_time:([0-9]+)"),
            "rdb_last_bgsave_status": Metric(MetricType.String, regex="rdb_last_bgsave_status:(.+)"),
            "rdb_last_bgsave_time_sec": Metric(MetricType.Integer, regex="rdb_last_bgsave_time_sec:([0-9]+)"),
            "total_connections_received": Metric(MetricType.Integer, regex="total_connections_received:([0-9]+)"),
            "total_commands_processed": Metric(MetricType.Integer, regex="total_commands_processed:([0-9]+)"),
            "rejected_connections": Metric(MetricType.Integer, regex="rejected_connections:([0-9]+)"),
            "expired_keys": Metric(MetricType.Integer, regex="expired_keys:([0-9]+)"),
            "evicted_keys": Metric(MetricType.Integer, regex="evicted_keys:([0-9]+)"),
            "keyspace_hits": Metric(MetricType.Integer, regex="keyspace_hits:([0-9]+)"),
            "keyspace_misses": Metric(MetricType.Integer, regex="keyspace_misses:([0-9]+)"),
            "connected_slaves": Metric(MetricType.Integer, regex="connected_slaves:([0-9]+)"),
            "master_repl_offset": Metric(MetricType.Integer, regex="master_repl_offset:([0-9]+)"),
            "used_cpu_sys": Metric(MetricType.Float, regex="used_cpu_sys:([0-9\.]+)"),
            "used_cpu_user": Metric(MetricType.Float, regex="used_cpu_user:([0-9\.]+)"),
            "used_cpu_sys_children": Metric(MetricType.Float, regex="used_cpu_sys_children:([0-9\.]+)"),
            "used_cpu_user_children": Metric(MetricType.Float, regex="used_cpu_user_children:([0-9\.]+)"),
            "keys": Metric(MetricType.Integer, self._filter_data, regex="keys=([0-9]+)"),
            "expires": Metric(MetricType.Integer, self._filter_data, regex="expires=([0-9]+)"),
            "avg_ttl": Metric(MetricType.Integer, self._filter_data, regex="avg_ttl=([0-9]+)"),
            "discovery": Metric(MetricType.Discovery, self._discovery),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.db = kwargs.get("db", None)
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.callback is not None:
            metric.callback()

        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        connector = SocketConnector(host=self.config.get("host", "localhost"),
                                    port=self.config.get("port", "6379"),
                                    command="info\r\nquit\r\n")

        self.test_data = connector.get().strip("\r")
        Cache.write(self.name, self.test_data)

    def _filter_data(self):
        if self.db is None:
            raise CheckFail("Required parameters not set (db)")

        position = self.test_data.index("# Keyspace")
        self.test_data = [value.strip()
                          for nr, value in enumerate(self.test_data[position:].split("\n"))
                          if "#" not in value and self.db in value and value.strip() != ""][0]

    def _discovery(self):
        position = self.test_data.index("# Keyspace")
        data = [value.strip().split(":", 2)[0]
                for nr, value in enumerate(self.test_data[position:].split("\n"))
                if "#" not in value and "keys" in value and value.strip() != ""]

        self.test_data = [{"{#DB}": item}
                          for item in data]
