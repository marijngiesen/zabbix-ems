import csv
from check import Check, CheckFail, MetricType, Metric
from lib.cache import Cache
from lib.utils import run_command, transpose_dict


class Dhcpd(Check):
    name = "dhcpd"
    first_ip = None
    tmpfile = None

    def _init_metrics(self):
        self.metrics = {
            "netname": Metric(MetricType.String, key="shared net name"),
            "first_ip": Metric(MetricType.String, key="first ip"),
            "last_ip": Metric(MetricType.String, key="last ip"),
            "pool_size": Metric(MetricType.Integer, key="max"),
            "active_leases": Metric(MetricType.Integer, key="cur"),
            "pool_usage": Metric(MetricType.Float, key="percent"),
            "expired_leases": Metric(MetricType.Integer, key="touch"),
            "failover_pool_size": Metric(MetricType.Integer, key="bu"),
            "failover_pool_percent": Metric(MetricType.Float, key="bu perc"),
            "discovery": Metric(MetricType.Discovery, self._discovery),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.first_ip = kwargs.get("firstip", None)

        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        if metric.type == MetricType.Discovery:
            metric.callback()
            return self._correct_type(metric.type, self.test_data)

        key = metric.kwargs.get("key")
        if self.first_ip is None:
            raise CheckFail("Required parameter 'firstip' missing.")
        if self.first_ip not in self.test_data:
            raise CheckFail("Specified first ip (%s) not found in data" % self.first_ip)

        return self._correct_type(metric.type, self.test_data[self.first_ip][key])

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        self._refresh_stats()
        self._parse_stats()

        Cache.write(self.name, self.test_data)

    def _refresh_stats(self):
        self.tmpfile = "/tmp/zems-dhcpd-unparsed"
        command = "%s -c %s -l %s -f c -o %s" % (self.config.get("dhcpd_pools_command", "/usr/bin/dhcpd-pools"),
                                                 self.config.get("dhcpd_config_file", "/etc/dhcpd/dhcpd.conf"),
                                                 self.config.get("dhcpd_leases_file", "/var/lib/dhcpd/dhcpd.leases"),
                                                 self.tmpfile)

        run_command(command)

    def _parse_stats(self):
        fieldnames = (
            "shared net name", "first ip", "last ip", "max", "cur", "percent", "touch", "t+c", "t+c perc", "bu",
            "bu perc")

        data = []
        with open(self.tmpfile, "r") as f:
            reader = csv.DictReader(f, fieldnames=fieldnames)

            # Skip the first two lines (as they are useless headers)
            reader.next()
            reader.next()
            for row in reader:
                # We only need the first section, dump the rest
                if ":" in row["shared net name"]:
                    break

                data.append(row)

        self.test_data = transpose_dict(data, "first ip")

    def _discovery(self):
        data = [{"{#FIRSTIP}": item[0], "{#LASTIP}": item[1]["last ip"]}
                for item in self.test_data.iteritems()]
        self.test_data = data
