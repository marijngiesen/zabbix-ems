from ConfigParser import ConfigParser
from check import Check, CheckFail, MetricType, Metric
from lib.fcgiconnector import FcgiConnector
from lib.utils import find_files_by_extension
from lib.cache import Cache


class PhpFpm(Check):
    name = "php-fpm"
    pool = None
    fpm_config = None

    def _init_metrics(self):
        self.metrics = {
            "pool": Metric(MetricType.String, regex="pool:\s*(.+)"),
            "process_manager": Metric(MetricType.String, regex="process manager:\s*(.+)"),
            "uptime": Metric(MetricType.Integer, regex="start since:\s*([0-9]+)"),
            "accepted_conn": Metric(MetricType.Integer, regex="accepted conn:\s*([0-9]+)"),
            "listen_queue": Metric(MetricType.Integer, regex="listen queue:\s*([0-9]+)"),
            "listen_queue_max": Metric(MetricType.Integer, regex="max listen queue:\s*([0-9]+)"),
            "listen_queue_len": Metric(MetricType.Integer, regex="listen queue len:\s*([0-9]+)"),
            "idle_processes": Metric(MetricType.Integer, regex="idle processes:\s*([0-9]+)"),
            "active_processes": Metric(MetricType.Integer, regex="active processes:\s*([0-9]+)"),
            "total_processes": Metric(MetricType.Integer, regex="total processes:\s*([0-9]+)"),
            "active_processes_max": Metric(MetricType.Integer, regex="max active processes:\s*([0-9]+)"),
            "max_children_reached": Metric(MetricType.Integer, regex="max children reached:\s*([0-9]+)"),
            "slow_requests": Metric(MetricType.Integer, regex="slow requests:\s*([0-9]+)"),
            "discovery": Metric(MetricType.Discovery, self._discovery),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.pool = kwargs.get("pool", None)

        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        self._read_fpm_config()

        if metric.type == MetricType.Discovery:
            metric.callback()
            return self._correct_type(metric.type, self.test_data)

        self._load_data()

        if self.pool is None:
            raise CheckFail("Required parameters not set (pool)")
        if self.pool not in self.fpm_config.sections():
            raise CheckFail("Pool %s does not exist in config files" % self.pool)
        if not self.fpm_config.has_option(self.pool, "pm.status_path"):
            raise CheckFail("Status path is not configured for pool %s" % self.pool)

        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        connector = self._get_connector()

        code, headers, self.test_data, error = connector.get()

        if not code.startswith("200"):
            raise CheckFail("Unable to get response: %s (code: %s)" % (error, code))

        Cache.write(self.name, self.test_data)

    def _read_fpm_config(self):
        if self.fpm_config is not None:
            return

        fpm_config_path = self.config.get("fpm_config_path", "/etc/php-fpm.d")

        self.fpm_config = ConfigParser()
        self.fpm_config.read(find_files_by_extension(fpm_config_path, "conf"))

        if len(self.fpm_config.sections()) == 0:
            self.logger.error("Can't read from PHP-FPM config")

    def _get_connector(self):
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

        return connector

    def _discovery(self):
        self.test_data = [{"{#POOL}": item} for item in self.fpm_config.sections()]
