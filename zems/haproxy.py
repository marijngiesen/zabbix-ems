from lib.socketcollector import *
from commandr import command
from check import Check, CheckFail, MetricType, Metric


class HAProxy(Check):
    name = "haproxy"
    pxname = None
    svname = None

    def _init_metrics(self):
        self.metrics = {
            "version": Metric("version", 1, MetricType.String, ":"),
            "uptime_sec": Metric("uptime_sec", 7, MetricType.Integer, ":"),
            "memmax_mb": Metric("memmax_mb", 8, MetricType.Integer, ":"),
            "maxsock": Metric("maxsock", 10, MetricType.Integer, ":"),
            "maxconn": Metric("maxconn", 11, MetricType.Integer, ":"),
            "maxpipes": Metric("maxpipes", 12, MetricType.Integer, ":"),
            "currconns": Metric("currconns", 13, MetricType.Integer, ":"),
            "pipesused": Metric("pipesused", 14, MetricType.Integer, ":"),
            "pipesfree": Metric("pipesfree", 15, MetricType.Integer, ":"),
            "tasks": Metric("tasks", 16, MetricType.Integer, ":"),
            "run_queue": Metric("run_queue", 17, MetricType.Integer, ":"),
            "node": Metric("node", 18, MetricType.String, ":"),
            "qcur": Metric("qcur", 2, MetricType.Integer, ",", self._filter_data),
            "qmax": Metric("qmax", 3, MetricType.Integer, ",", self._filter_data),
            "scur": Metric("scur", 4, MetricType.Integer, ",", self._filter_data),
            "smax": Metric("smax", 5, MetricType.Integer, ",", self._filter_data),
            "slim": Metric("slim", 6, MetricType.Integer, ",", self._filter_data),
            "stot": Metric("stot", 7, MetricType.Integer, ",", self._filter_data),
            "bin": Metric("bin", 8, MetricType.Integer, ",", self._filter_data),
            "bout": Metric("bout", 9, MetricType.Integer, ",", self._filter_data),
            "dreq": Metric("dreq", 10, MetricType.Integer, ",", self._filter_data),
            "dresp": Metric("dresp", 11, MetricType.Integer, ",", self._filter_data),
            "ereq": Metric("ereq", 12, MetricType.Integer, ",", self._filter_data),
            "econ": Metric("econ", 13, MetricType.Integer, ",", self._filter_data),
            "eresp": Metric("eresp", 14, MetricType.Integer, ",", self._filter_data),
            "wretr": Metric("wretr", 15, MetricType.Integer, ",", self._filter_data),
            "wredis": Metric("wredis", 16, MetricType.Integer, ",", self._filter_data),
            "status": Metric("status", 17, MetricType.String, ",", self._filter_data),
            "weight": Metric("weight", 18, MetricType.Integer, ",", self._filter_data),
            "act": Metric("act", 19, MetricType.String, ",", self._filter_data),
            "bck": Metric("bck", 20, MetricType.String, ",", self._filter_data),
            "chkfail": Metric("chkfail", 21, MetricType.String, ",", self._filter_data),
            "chkdown": Metric("chkdown", 22, MetricType.String, ",", self._filter_data),
            "lastchg": Metric("lastchg", 23, MetricType.String, ",", self._filter_data),
            "downtime": Metric("downtime", 24, MetricType.String, ",", self._filter_data),
            "qlimit": Metric("qlimit", 25, MetricType.String, ",", self._filter_data),
            "pid": Metric("pid", 26, MetricType.String, ",", self._filter_data),
            "iid": Metric("iid", 27, MetricType.String, ",", self._filter_data),
            "sid": Metric("sid", 28, MetricType.String, ",", self._filter_data),
            "throttle": Metric("throttle", 29, MetricType.String, ",", self._filter_data),
            "lbtot": Metric("lbtot", 30, MetricType.Integer, ",", self._filter_data),
            "tracked": Metric("tracked", 31, MetricType.String, ",", self._filter_data),
            "type": Metric("type", 32, MetricType.String, ",", self._filter_data),
            "rate": Metric("rate", 33, MetricType.String, ",", self._filter_data),
            "rate_lim": Metric("rate_lim", 34, MetricType.String, ",", self._filter_data),
            "rate_max": Metric("rate_max", 35, MetricType.String, ",", self._filter_data),
            "check_status": Metric("check_status", 36, MetricType.String, ",", self._filter_data),
            "check_code": Metric("check_code", 37, MetricType.String, ",", self._filter_data),
            "check_duration": Metric("check_duration", 38, MetricType.String, ",", self._filter_data),
            "hrsp_1xx": Metric("hrsp_1xx", 39, MetricType.String, ",", self._filter_data),
            "hrsp_2xx": Metric("hrsp_2xx", 40, MetricType.String, ",", self._filter_data),
            "hrsp_3xx": Metric("hrsp_3xx", 41, MetricType.String, ",", self._filter_data),
            "hrsp_4xx": Metric("hrsp_4xx", 42, MetricType.String, ",", self._filter_data),
            "hrsp_5xx": Metric("hrsp_5xx", 43, MetricType.String, ",", self._filter_data),
            "hrsp_other": Metric("hrsp_other", 44, MetricType.String, ",", self._filter_data),
            "hanafail": Metric("hanafail", 45, MetricType.String, ",", self._filter_data),
            "req_rate": Metric("req_rate", 46, MetricType.String, ",", self._filter_data),
            "req_rate_max": Metric("req_rate_max", 47, MetricType.String, ",", self._filter_data),
            "req_tot": Metric("req_tot", 48, MetricType.String, ",", self._filter_data),
            "cli_abrt": Metric("cli_abrt", 49, MetricType.String, ",", self._filter_data),
            "srv_abrt": Metric("srv_abrt", 50, MetricType.String, ",", self._filter_data),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.pxname = kwargs.get("pxname", None)
        self.svname = kwargs.get("svname", None)

        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        if metric.filter_callback is not None:
            metric.filter_callback(metric.separator)
            value = self.test_data[metric.position]
        else:
            value = self.test_data[metric.position].split(metric.separator)[1]

        return self._correct_type(metric.type, value)

    def _load_data(self):
        if self.test_data is not None:
            return self.test_data

        collector = SocketCollector(socket_file=self.config.get("socket", "/var/lib/haproxy/stats.sock"),
                                    command="show info\nshow stat\n")

        return collector.get().split("\n")

    def _filter_data(self, separator):
        if self.pxname is None or self.svname is None:
            raise CheckFail("Required parameters not set (pxname, svname)")

        for id, line in enumerate(self.test_data):
            values = line.split(separator)
            if self.pxname in values and self.svname in values:
                self.test_data = values

@command("haproxy")
def haproxy(key=None, pxname=None, svname=None):
    test = HAProxy()

    if key is not None:
        test.need_root()
        test.get(key, pxname=pxname, svname=svname)
    else:
        test.print_metrics()


