from lib.socketconnector import *
from check import Check, CheckFail, MetricType, Metric
from lib.cache import Cache


class Radiator(Check):
    name = "radiator"

    def _init_metrics(self):
        self.metrics = {
            "access_accepts": Metric(MetricType.Integer, regex="Access accepts:([0-9]+)"),
            "access_challenges": Metric(MetricType.Integer, regex="Access challenges:([0-9]+)"),
            "access_rejects": Metric(MetricType.Integer, regex="Access rejects:([0-9]+)"),
            "access_requests": Metric(MetricType.Integer, regex="Access requests:([0-9]+)"),
            "access_requests_dropped_": Metric(MetricType.Integer, regex="Dropped access requests:([0-9]+)"),
            "access_requests_duplicate": Metric(MetricType.Integer, regex="Duplicate access requests:([0-9]+)"),
            "access_requests_malformed": Metric(MetricType.Integer, regex="Malformed access requests:([0-9]+)"),
            "accounting_requests": Metric(MetricType.Integer, regex="Accounting requests:([0-9]+)"),
            "accounting_responses": Metric(MetricType.Integer, regex="Accounting responses:([0-9]+)"),
            "accounting_requests_dropped": Metric(MetricType.Integer, regex="Dropped accounting requests:([0-9]+)"),
            "accounting_requests_duplicate": Metric(MetricType.Integer, regex="Duplicate accounting requests:([0-9]+)"),
            "accounting_requests_malformed": Metric(MetricType.Integer, regex="Malformed accounting requests:([0-9]+)"),
            "bad_auth_authentication": Metric(MetricType.Integer,
                                              regex="Bad authenticators in authentication requests:([0-9]+)"),
            "bad_auth_accounting": Metric(MetricType.Integer,
                                          regex="Bad authenticators in accounting requests:([0-9]+)"),
            "bad_auth_total": Metric(MetricType.Integer, regex="Total Bad authenticators in requests:([0-9]+)"),
            "requests_dropped_total": Metric(MetricType.Integer, regex="Total dropped requests:([0-9]+)"),
            "requests_duplicate_total": Metric(MetricType.Integer, regex="Total duplicate requests:([0-9]+)"),
            "requests_proxied_noreply": Metric(MetricType.Integer,
                                               regex="Total proxied requests with no reply:([0-9]+)"),
            "requests_proxied_total": Metric(MetricType.Integer, regex="Total proxied requests:([0-9]+)"),
            "requests_total": Metric(MetricType.Integer, regex="Total requests:([0-9]+)"),
            "avg_response_time": Metric(MetricType.Float, regex="Average response time:([0-9\.]+)"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        connector = SocketConnector(host=self.config.get("host", "127.0.0.1"),
                                    port=self.config.get("port", 9002),
                                    command="LOGIN %s %s\nSTATS .\nQUIT\n" % (
                                        self.config.get("user", ""), self.config.get("passwd", "")))

        self.test_data = connector.get()
        Cache.write(self.name, self.test_data)
