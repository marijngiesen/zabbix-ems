from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from lib.cache import Cache


class HAProxy(Check):
    name = "haproxy"
    pxname = None
    svname = None

    def _init_metrics(self):
        self.metrics = {
            "version": Metric("version", MetricType.String, 1, ":"),
            "uptime_sec": Metric("uptime_sec", MetricType.Integer, 7, ":"),
            "memmax_mb": Metric("memmax_mb", MetricType.Integer, 8, ":"),
            "maxsock": Metric("maxsock", MetricType.Integer, 10, ":"),
            "maxconn": Metric("maxconn", MetricType.Integer, 11, ":"),
            "maxpipes": Metric("maxpipes", MetricType.Integer, 12, ":"),
            "currconns": Metric("currconns", MetricType.Integer, 13, ":"),
            "pipesused": Metric("pipesused", MetricType.Integer, 14, ":"),
            "pipesfree": Metric("pipesfree", MetricType.Integer, 15, ":"),
            "tasks": Metric("tasks", MetricType.Integer, 16, ":"),
            "run_queue": Metric("run_queue", MetricType.Integer, 17, ":"),
            "node": Metric("node", MetricType.String, 18, ":"),
            "qcur": Metric("qcur", MetricType.Integer, 2, ",", self._filter_data),
            "qmax": Metric("qmax", MetricType.Integer, 3, ",", self._filter_data),
            "scur": Metric("scur", MetricType.Integer, 4, ",", self._filter_data),
            "smax": Metric("smax", MetricType.Integer, 5, ",", self._filter_data),
            "slim": Metric("slim", MetricType.Integer, 6, ",", self._filter_data),
            "stot": Metric("stot", MetricType.Integer, 7, ",", self._filter_data),
            "bin": Metric("bin", MetricType.Integer, 8, ",", self._filter_data),
            "bout": Metric("bout", MetricType.Integer, 9, ",", self._filter_data),
            "dreq": Metric("dreq", MetricType.Integer, 10, ",", self._filter_data),
            "dresp": Metric("dresp", MetricType.Integer, 11, ",", self._filter_data),
            "ereq": Metric("ereq", MetricType.Integer, 12, ",", self._filter_data),
            "econ": Metric("econ", MetricType.Integer, 13, ",", self._filter_data),
            "eresp": Metric("eresp", MetricType.Integer, 14, ",", self._filter_data),
            "wretr": Metric("wretr", MetricType.Integer, 15, ",", self._filter_data),
            "wredis": Metric("wredis", MetricType.Integer, 16, ",", self._filter_data),
            "status": Metric("status", MetricType.String, 17, ",", self._filter_data),
            "weight": Metric("weight", MetricType.Integer, 18, ",", self._filter_data),
            "act": Metric("act", MetricType.String, 19, ",", self._filter_data),
            "bck": Metric("bck", MetricType.String, 20, ",", self._filter_data),
            "chkfail": Metric("chkfail", MetricType.String, 21, ",", self._filter_data),
            "chkdown": Metric("chkdown", MetricType.String, 22, ",", self._filter_data),
            "lastchg": Metric("lastchg", MetricType.String, 23, ",", self._filter_data),
            "downtime": Metric("downtime", MetricType.String, 24, ",", self._filter_data),
            "qlimit": Metric("qlimit", MetricType.String, 25, ",", self._filter_data),
            "pid": Metric("pid", MetricType.String, 26, ",", self._filter_data),
            "iid": Metric("iid", MetricType.String, 27, ",", self._filter_data),
            "sid": Metric("sid", MetricType.String, 28, ",", self._filter_data),
            "throttle": Metric("throttle", MetricType.String, 29, ",", self._filter_data),
            "lbtot": Metric("lbtot", MetricType.Integer, 30, ",", self._filter_data),
            "tracked": Metric("tracked", MetricType.String, 31, ",", self._filter_data),
            "type": Metric("type", MetricType.String, 32, ",", self._filter_data),
            "rate": Metric("rate", MetricType.String, 33, ",", self._filter_data),
            "rate_lim": Metric("rate_lim", MetricType.String, 34, ",", self._filter_data),
            "rate_max": Metric("rate_max", MetricType.String, 35, ",", self._filter_data),
            "check_status": Metric("check_status", MetricType.String, 36, ",", self._filter_data),
            "check_code": Metric("check_code", MetricType.String, 37, ",", self._filter_data),
            "check_duration": Metric("check_duration", MetricType.String, 38, ",", self._filter_data),
            "hrsp_1xx": Metric("hrsp_1xx", MetricType.String, 39, ",", self._filter_data),
            "hrsp_2xx": Metric("hrsp_2xx", MetricType.String, 40, ",", self._filter_data),
            "hrsp_3xx": Metric("hrsp_3xx", MetricType.String, 41, ",", self._filter_data),
            "hrsp_4xx": Metric("hrsp_4xx", MetricType.String, 42, ",", self._filter_data),
            "hrsp_5xx": Metric("hrsp_5xx", MetricType.String, 43, ",", self._filter_data),
            "hrsp_other": Metric("hrsp_other", MetricType.String, 44, ",", self._filter_data),
            "hanafail": Metric("hanafail", MetricType.String, 45, ",", self._filter_data),
            "req_rate": Metric("req_rate", MetricType.String, 46, ",", self._filter_data),
            "req_rate_max": Metric("req_rate_max", MetricType.String, 47, ",", self._filter_data),
            "req_tot": Metric("req_tot", MetricType.String, 48, ",", self._filter_data),
            "cli_abrt": Metric("cli_abrt", MetricType.String, 49, ",", self._filter_data),
            "srv_abrt": Metric("srv_abrt", MetricType.String, 50, ",", self._filter_data),
            "discovery": Metric("discovery", MetricType.Discovery, 1, ",", self._discovery),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.pxname = kwargs.get("pxname", None)
        self.svname = kwargs.get("svname", None)

        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.filter_callback is not None:
            if metric.type == MetricType.Discovery:
                metric.filter_callback()
                return self._correct_type(metric.type, self.test_data)
            else:
                metric.filter_callback(metric.separator)
                return self._correct_type(metric.type, self.test_data[metric.position])
        else:
            return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return self.test_data

        connector = SocketConnector(socket_file=self.config.get("socket", "/var/lib/haproxy/stats.sock"),
                                    command="show info\nshow stat\n")

        data = connector.get()
        Cache.write(self.name, data)

        return data.split("\n")

    def _filter_data(self, separator):
        if self.pxname is None or self.svname is None:
            raise CheckFail("Required parameters not set (pxname, svname)")

        for id, line in enumerate(self.test_data):
            values = line.split(separator)
            if self.pxname in values and self.svname in values:
                self.test_data = values

    def _discovery(self):
        data = [value.strip().split(",", 2)[0:2]
                for nr, value in enumerate(self.test_data[22:])
                if "#" not in value and value.strip() != ""]

        self.test_data = [{"{#PROXY}": item[0], "{#SERVER}": item[1]}
                          for item in data]
