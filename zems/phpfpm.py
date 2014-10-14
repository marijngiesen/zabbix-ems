from ConfigParser import ConfigParser

from check import Check, CheckFail, MetricType, Metric
from lib.fcgiconnector import FcgiConnector
from lib import utils
from zems.lib.cache import Cache


class PhpFpm(Check):
    name = "php-fpm"
    pool = None
    fpm_config = None

    def _init_metrics(self):
        self.metrics = {
            "pool": Metric("pool", 0, MetricType.String, ":"),
            "process_manager": Metric("process manager", 1, MetricType.String, ":"),
            "start_since": Metric("start since", 3, MetricType.Integer, ":"),
            "accepted_conn": Metric("accepted conn", 4, MetricType.String, ":"),
            "listen_queue": Metric("listen queue", 5, MetricType.Integer, ":"),
            "listen_queue_max": Metric("max listen queue", 6, MetricType.Integer, ":"),
            "listen_queue_len": Metric("listen queue len", 7, MetricType.Integer, ":"),
            "idle_processes": Metric("idle processes", 8, MetricType.Integer, ":"),
            "active_processes": Metric("active processes", 9, MetricType.Integer, ":"),
            "total_processes": Metric("total processes", 10, MetricType.Integer, ":"),
            "active_processes_max": Metric("max active processes", 11, MetricType.Integer, ":"),
            "max_children_reached": Metric("max children reached", 12, MetricType.Integer, ":"),
            "slow_requests": Metric("slow requests", 13, MetricType.Integer, ":"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.pool = kwargs.get("pool", None)
        if self.pool is None:
            raise CheckFail("Required parameters not set (pool)")

        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        self._read_fpm_config()

        listen = self.fpm_config.get(self.pool, "listen")
        status_path = self.fpm_config.get(self.pool, "pm.status_path")
        if listen.startswith("/"):
            connector = FcgiConnector(socket_file=listen, uri=status_path)
        else:
            if ":" in listen:
                host, port = listen.split(":")
                connector = FcgiConnector(host=host, port=port, uri=status_path)
            else:
                connector = FcgiConnector(port=listen, host="127.0.0.1", uri=status_path)

        code, headers, data, error = connector.get()

        if not code.startswith("200"):
            self.logger.error("status: got response, but not correct")
            return None

        Cache.write(self.name, data)

        return data.split("\n")

    def _read_fpm_config(self):
        if self.fpm_config is not None:
            return

        fpm_config_path = self.config.get("fpm_config_path", "/etc/php-fpm.d")

        self.fpm_config = ConfigParser()
        self.fpm_config.read(utils.find_files_by_extension(fpm_config_path, "conf"))

        if len(self.fpm_config.sections()) == 0:
            self.logger.error("Can't read from PHP-FPM config")

        if self.pool not in self.fpm_config.sections():
            raise CheckFail("Pool %s does not exist in config files" % self.pool)

        if not self.fpm_config.has_option(self.pool, "pm.status_path"):
            raise CheckFail("Status path is not configured for pool %s" % self.pool)
