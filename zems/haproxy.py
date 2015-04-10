from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from lib.cache import Cache


class HAProxy(Check):
    name = "haproxy"
    pxname = None
    svname = None

    def _init_metrics(self):
        self.metrics = {
            "version": Metric(MetricType.String, regex="Version: ([0-9\.]+)"),
            "uptime_sec": Metric(MetricType.Integer, regex="Uptime_sec: ([0-9]+)"),
            "memmax_mb": Metric(MetricType.Integer, regex="Memmax_MB: ([0-9]+)"),
            "maxsock": Metric(MetricType.Integer, regex="Maxsock: ([0-9]+)"),
            "maxconn": Metric(MetricType.Integer, regex="Maxconn: ([0-9]+)"),
            "maxpipes": Metric(MetricType.Integer, regex="Maxpipes: ([0-9]+)"),
            "currconns": Metric(MetricType.Integer, regex="CurrConns: ([0-9]+)"),
            "currsslconns": Metric(MetricType.Integer, regex="CurrSslConns: ([0-9]+)"),
            "pipesused": Metric(MetricType.Integer, regex="PipesUsed: ([0-9]+)"),
            "pipesfree": Metric(MetricType.Integer, regex="PipesFree: ([0-9]+)"),
            "connrate": Metric(MetricType.Integer, regex="ConnRate: ([0-9]+)"),
            "sessrate": Metric(MetricType.Integer, regex="SessRate: ([0-9]+)"),
            "sslrate": Metric(MetricType.Integer, regex="SslRate: ([0-9]+)"),
            "tasks": Metric(MetricType.Integer, regex="Tasks: ([0-9]+)"),
            "run_queue": Metric(MetricType.Integer, regex="Run_queue: ([0-9]+)"),
            "idle_pct": Metric(MetricType.Integer, regex="Idle_pct: ([0-9]+)"),
            "node": Metric(MetricType.String, regex="node: (.+)"),
            "qcur": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=2),
            "qmax": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=3),
            "scur": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=4),
            "smax": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=5),
            "slim": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=6),
            "stot": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=7),
            "bin": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=8),
            "bout": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=9),
            "dreq": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=10),
            "dresp": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=11),
            "ereq": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=12),
            "econ": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=12),
            "eresp": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=14),
            "wretr": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=15),
            "wredis": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=16),
            "status": Metric(MetricType.String, callback=self._filter_data, separator=",", position=17),
            "weight": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=18),
            "act": Metric(MetricType.String, callback=self._filter_data, separator=",", position=19),
            "bck": Metric(MetricType.String, callback=self._filter_data, separator=",", position=20),
            "chkfail": Metric(MetricType.String, callback=self._filter_data, separator=",", position=21),
            "chkdown": Metric(MetricType.String, callback=self._filter_data, separator=",", position=22),
            "lastchg": Metric(MetricType.String, callback=self._filter_data, separator=",", position=23),
            "downtime": Metric(MetricType.String, callback=self._filter_data, separator=",", position=24),
            "qlimit": Metric(MetricType.String, callback=self._filter_data, separator=",", position=25),
            "pid": Metric(MetricType.String, callback=self._filter_data, separator=",", position=26),
            "iid": Metric(MetricType.String, callback=self._filter_data, separator=",", position=27),
            "sid": Metric(MetricType.String, callback=self._filter_data, separator=",", position=28),
            "throttle": Metric(MetricType.String, callback=self._filter_data, separator=",", position=29),
            "lbtot": Metric(MetricType.Integer, callback=self._filter_data, separator=",", position=30),
            "tracked": Metric(MetricType.String, callback=self._filter_data, separator=",", position=31),
            "type": Metric(MetricType.String, callback=self._filter_data, separator=",", position=32),
            "rate": Metric(MetricType.String, callback=self._filter_data, separator=",", position=33),
            "rate_lim": Metric(MetricType.String, callback=self._filter_data, separator=",", position=34),
            "rate_max": Metric(MetricType.String, callback=self._filter_data, separator=",", position=35),
            "check_status": Metric(MetricType.String, callback=self._filter_data, separator=",", position=36),
            "check_code": Metric(MetricType.String, callback=self._filter_data, separator=",", position=37),
            "check_duration": Metric(MetricType.String, callback=self._filter_data, separator=",", position=38),
            "hrsp_1xx": Metric(MetricType.String, callback=self._filter_data, separator=",", position=39),
            "hrsp_2xx": Metric(MetricType.String, callback=self._filter_data, separator=",", position=40),
            "hrsp_3xx": Metric(MetricType.String, callback=self._filter_data, separator=",", position=41),
            "hrsp_4xx": Metric(MetricType.String, callback=self._filter_data, separator=",", position=42),
            "hrsp_5xx": Metric(MetricType.String, callback=self._filter_data, separator=",", position=43),
            "hrsp_other": Metric(MetricType.String, callback=self._filter_data, separator=",", position=44),
            "hanafail": Metric(MetricType.String, callback=self._filter_data, separator=",", position=45),
            "req_rate": Metric(MetricType.String, callback=self._filter_data, separator=",", position=46),
            "req_rate_max": Metric(MetricType.String, callback=self._filter_data, separator=",", position=47),
            "req_tot": Metric(MetricType.String, callback=self._filter_data, separator=",", position=48),
            "cli_abrt": Metric(MetricType.String, callback=self._filter_data, separator=",", position=49),
            "srv_abrt": Metric(MetricType.String, callback=self._filter_data, separator=",", position=50),
            "discovery": Metric(MetricType.Discovery, self._discovery),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.pxname = kwargs.get("pxname", None)
        self.svname = kwargs.get("svname", None)

        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.type == MetricType.Discovery or metric.callback is not None:
            metric.callback()

        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        connector = SocketConnector(socket_file=self.config.get("socket", "/var/lib/haproxy/stats.sock"),
                                    command="show info\nshow stat\n")

        self.test_data = connector.get()
        Cache.write(self.name, self.test_data)

    def _filter_data(self):
        if self.pxname is None or self.svname is None:
            raise CheckFail("Required parameters not set (pxname, svname)")

        for nr, line in enumerate(self.test_data.split("\n")):
            if self.pxname in line and self.svname in line:
                self.test_data = line

    def _discovery(self):
        position = self.test_data.index("#")
        data = [value.strip().split(",", 2)[0:2]
                for nr, value in enumerate(self.test_data[position:].split("\n"))
                if "#" not in value and value.strip() != ""]

        self.test_data = [{"{#PROXY}": item[0], "{#SERVER}": item[1]}
                          for item in data]
