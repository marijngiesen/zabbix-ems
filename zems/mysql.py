from check import Check, MetricType, Metric
from lib.mysqlconnector import MySQLConnector, MySQLConnectorException
from lib.cache import Cache
from lib.utils import dict_has_item, dict_keys_to_lower

class MySQL(Check):
    name = "mysql"
    connector = None

    def _init_metrics(self):
        self.metrics = {
            "key_read_requests": Metric(MetricType.Integer, key="key_read_requests"),
            "key_reads": Metric(MetricType.Integer, key="key_reads"),
            "key_write_requests": Metric(MetricType.Integer, key="key_write_requests"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        key = metric.kwargs.get("key")
        return self._correct_type(metric.type, self.test_data[key])

    def _load_data(self):
        # self.test_data = Cache.read(self.name)
        # if self.test_data is not None:
        # return

        self._init_connector()

        self.test_data = {}
        self._get_global_status()
        self._get_variables()

        if self.config.get("check_slave", True):
            self._get_slave_status()

        if self.config.get("check_master", True) and dict_has_item(self.test_data, "log_bin", "ON"):
            self._get_master_status()

        # if self.config.get("check_procs", True):
        #     self._get_processlist()
        #
        # if self.config.get("check_innodb", True):
        #     self._get_innodb_status()
        #
        # if self.config.get("check_qrt", True):
        #     self._get_percona_qrt()

        Cache.write(self.name, self.test_data)

    def _init_connector(self):
        if self.connector is not None:
            return

        socket_file = self.config.get("socket_file", None)
        if socket_file is not None:
            self.connector = MySQLConnector(socket_file=socket_file, user=self.config.get("user", "root"),
                                            passwd=self.config.get("passwd", ""))
        else:
            self.connector = MySQLConnector(host=self.config.get("host", "127.0.0.1"),
                                            port=self.config.get("port", 3306),
                                            user=self.config.get("user", "root"), passwd=self.config.get("passwd", ""))

    def _get_global_status(self):
        self.test_data.update(self._format_data(self.connector.get("SHOW /*!50002 GLOBAL */ STATUS")))

    def _get_variables(self):
        self.test_data.update(self._format_data(self.connector.get("SHOW VARIABLES")))

    def _get_slave_status(self):
        slave_status = self.connector.get("SHOW SLAVE STATUS")[0]
        if len(slave_status) < 1:
            return

        slave_status = dict_keys_to_lower(slave_status)
        self.test_data["relay_log_space"] = slave_status["relay_log_space"]
        self.test_data["slave_lag"] = slave_status["seconds_behind_master"]
        self.test_data["slave_running"] = int(slave_status["slave_sql_running"] == "Yes")

        heartbeat_table = self.config.get("heartbeat", "")
        if len(heartbeat_table) > 0:
            try:
                replication_status = self.connector.get(
                    "SELECT GREATEST(0, UNIX_TIMESTAMP() - UNIX_TIMESTAMP(ts) - 1) AS delay "
                    "FROM %s WHERE server_id = %s"
                    % (heartbeat_table, self.config.get("master_id", "1")))

                self.test_data["slave_lag"] = replication_status["delay"]
            except MySQLConnectorException, e:
                self.logger.exception("Unable to get data from heartbeat table '%s'. Error: %s" % (heartbeat_table, e))

    def _get_master_status(self):
        master_logs = self.connector.get("SHOW MASTER LOGS")
        if len(master_logs) < 1:
            return

        for log in master_logs:
            log = dict_keys_to_lower(log)


    def _get_processlist(self):
        processlist = self.connector.get("SHOW PROCESSLIST")

    def _get_innodb_status(self):
        innodb_status = self.connector.get("SHOW /*!50000 ENGINE*/ INNODB STATUS")

    def _get_percona_qrt(self):
        percona_qrt = self.connector.get("SELECT `count`, total * 1000000 AS total "
                                         "FROM INFORMATION_SCHEMA.QUERY_RESPONSE_TIME WHERE `time` <> 'TOO LONG'")

    def _format_data(self, data, key_column="Variable_name", value_column="Value"):
        tmp = {}
        for value in data:
            tmp[value[key_column].lower()] = value[value_column]

        return tmp

