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
            "key_writes": Metric(MetricType.Integer, key="key_writes"),
            "history_list": Metric(MetricType.Integer, key="history_list"),
            "innodb_transactions": Metric(MetricType.Integer, key="innodb_transactions"),
            "read_views": Metric(MetricType.Integer, key="read_views"),
            "current_transactions": Metric(MetricType.Integer, key="current_transactions"),
            "locked_transactions": Metric(MetricType.Integer, key="locked_transactions"),
            "active_transactions": Metric(MetricType.Integer, key="active_transactions"),
            "pool_size": Metric(MetricType.Integer, key="pool_size"),
            "free_pages": Metric(MetricType.Integer, key="free_pages"),
            "database_pages": Metric(MetricType.Integer, key="database_pages"),
            "modified_pages": Metric(MetricType.Integer, key="modified_pages"),
            "pages_read": Metric(MetricType.Integer, key="pages_read"),
            "pages_created": Metric(MetricType.Integer, key="pages_created"),
            "pages_written": Metric(MetricType.Integer, key="pages_written"),
            "file_fsyncs": Metric(MetricType.Integer, key="file_fsyncs"),
            "file_reads": Metric(MetricType.Integer, key="file_reads"),
            "file_writes": Metric(MetricType.Integer, key="file_writes"),
            "log_writes": Metric(MetricType.Integer, key="log_writes"),
            "pending_aio_log_ios": Metric(MetricType.Integer, key="pending_aio_log_ios"),
            "pending_aio_sync_ios": Metric(MetricType.Integer, key="pending_aio_sync_ios"),
            "pending_buf_pool_flushes": Metric(MetricType.Integer, key="pending_buf_pool_flushes"),
            "pending_chkp_writes": Metric(MetricType.Integer, key="pending_chkp_writes"),
            "pending_ibuf_aio_reads": Metric(MetricType.Integer, key="pending_ibuf_aio_reads"),
            "pending_log_flushes": Metric(MetricType.Integer, key="pending_log_flushes"),
            "pending_log_writes": Metric(MetricType.Integer, key="pending_log_writes"),
            "pending_normal_aio_reads": Metric(MetricType.Integer, key="pending_normal_aio_reads"),
            "pending_normal_aio_writes": Metric(MetricType.Integer, key="pending_normal_aio_writes"),
            "ibuf_inserts": Metric(MetricType.Integer, key="ibuf_inserts"),
            "ibuf_merged": Metric(MetricType.Integer, key="ibuf_merged"),
            "ibuf_merges": Metric(MetricType.Integer, key="ibuf_merges"),
            "spin_waits": Metric(MetricType.Integer, key="spin_waits"),
            "spin_rounds": Metric(MetricType.Integer, key="spin_rounds"),
            "os_waits": Metric(MetricType.Integer, key="os_waits"),
            "rows_inserted": Metric(MetricType.Integer, key="rows_inserted"),
            "rows_updated": Metric(MetricType.Integer, key="rows_updated"),
            "rows_deleted": Metric(MetricType.Integer, key="rows_deleted"),
            "rows_read": Metric(MetricType.Integer, key="rows_read"),
            "table_locks_waited": Metric(MetricType.Integer, key="table_locks_waited"),
            "table_locks_immediate": Metric(MetricType.Integer, key="table_locks_immediate"),
            "slow_queries": Metric(MetricType.Integer, key="slow_queries"),
            "open_files": Metric(MetricType.Integer, key="open_files"),
            "open_tables": Metric(MetricType.Integer, key="open_tables"),
            "opened_tables": Metric(MetricType.Integer, key="opened_tables"),
            "innodb_open_files": Metric(MetricType.Integer, key="innodb_open_files"),
            "open_files_limit": Metric(MetricType.Integer, key="open_files_limit"),
            "table_open_cache": Metric(MetricType.Integer, key="table_open_cache"),
            "aborted_clients": Metric(MetricType.Integer, key="aborted_clients"),
            "aborted_connects": Metric(MetricType.Integer, key="aborted_connects"),
            "max_used_connections": Metric(MetricType.Integer, key="max_used_connections"),
            "slow_launch_threads": Metric(MetricType.Integer, key="slow_launch_threads"),
            "threads_cached": Metric(MetricType.Integer, key="threads_cached"),
            "threads_connected": Metric(MetricType.Integer, key="threads_connected"),
            "threads_created": Metric(MetricType.Integer, key="threads_created"),
            "threads_running": Metric(MetricType.Integer, key="threads_running"),
            "max_connections": Metric(MetricType.Integer, key="max_connections"),
            "thread_cache_size": Metric(MetricType.Integer, key="thread_cache_size"),
            "connections": Metric(MetricType.Integer, key="connections"),
            "slave_running": Metric(MetricType.Integer, key="slave_running"),
            "slave_retried_transactions": Metric(MetricType.Integer, key="slave_retried_transactions"),
            "slave_lag": Metric(MetricType.Integer, key="slave_lag"),
            "slave_open_temp_tables": Metric(MetricType.Integer, key="slave_open_temp_tables"),
            "qcache_free_blocks": Metric(MetricType.Integer, key="qcache_free_blocks"),
            "qcache_free_memory": Metric(MetricType.Integer, key="qcache_free_memory"),
            "qcache_hits": Metric(MetricType.Integer, key="qcache_hits"),
            "qcache_inserts": Metric(MetricType.Integer, key="qcache_inserts"),
            "qcache_lowmem_prunes": Metric(MetricType.Integer, key="qcache_lowmem_prunes"),
            "qcache_not_cached": Metric(MetricType.Integer, key="qcache_not_cached"),
            "qcache_queries_in_cache": Metric(MetricType.Integer, key="qcache_queries_in_cache"),
            "qcache_total_blocks": Metric(MetricType.Integer, key="qcache_total_blocks"),
            "query_cache_size": Metric(MetricType.Integer, key="query_cache_size"),
            "questions": Metric(MetricType.Integer, key="questions"),
            "com_update": Metric(MetricType.Integer, key="com_update"),
            "com_insert": Metric(MetricType.Integer, key="com_insert"),
            "com_select": Metric(MetricType.Integer, key="com_select"),
            "com_delete": Metric(MetricType.Integer, key="com_delete"),
            "com_replace": Metric(MetricType.Integer, key="com_replace"),
            "com_load": Metric(MetricType.Integer, key="com_load"),
            "com_update_multi": Metric(MetricType.Integer, key="com_update_multi"),
            "com_insert_select": Metric(MetricType.Integer, key="com_insert_select"),
            "com_delete_multi": Metric(MetricType.Integer, key="com_delete_multi"),
            "com_replace_select": Metric(MetricType.Integer, key="com_replace_select"),
            "select_full_join": Metric(MetricType.Integer, key="select_full_join"),
            "select_full_range_join": Metric(MetricType.Integer, key="select_full_range_join"),
            "select_range": Metric(MetricType.Integer, key="select_range"),
            "select_range_check": Metric(MetricType.Integer, key="select_range_check"),
            "select_scan": Metric(MetricType.Integer, key="select_scan"),
            "sort_merge_passes": Metric(MetricType.Integer, key="sort_merge_passes"),
            "sort_range": Metric(MetricType.Integer, key="sort_range"),
            "sort_rows": Metric(MetricType.Integer, key="sort_rows"),
            "sort_scan": Metric(MetricType.Integer, key="sort_scan"),
            "created_tmp_tables": Metric(MetricType.Integer, key="created_tmp_tables"),
            "created_tmp_disk_tables": Metric(MetricType.Integer, key="created_tmp_disk_tables"),
            "created_tmp_files": Metric(MetricType.Integer, key="created_tmp_files"),
            "bytes_sent": Metric(MetricType.Integer, key="bytes_sent"),
            "bytes_received": Metric(MetricType.Integer, key="bytes_received"),
            "innodb_log_buffer_size": Metric(MetricType.Integer, key="innodb_log_buffer_size"),
            "unflushed_log": Metric(MetricType.Integer, key="unflushed_log"),
            "log_bytes_flushed": Metric(MetricType.Integer, key="log_bytes_flushed"),
            "log_bytes_written": Metric(MetricType.Integer, key="log_bytes_written"),
            "relay_log_space": Metric(MetricType.Integer, key="relay_log_space"),
            "binlog_cache_size": Metric(MetricType.Integer, key="binlog_cache_size"),
            "binlog_cache_disk_use": Metric(MetricType.Integer, key="binlog_cache_disk_use"),
            "binlog_cache_use": Metric(MetricType.Integer, key="binlog_cache_use"),
            "binary_log_space": Metric(MetricType.Integer, key="binary_log_space"),
            "innodb_locked_tables": Metric(MetricType.Integer, key="innodb_locked_tables"),
            "innodb_lock_structs": Metric(MetricType.Integer, key="innodb_lock_structs"),
            "state_closing_tables": Metric(MetricType.Integer, key="state_closing_tables"),
            "state_copying_to_tmp_table": Metric(MetricType.Integer, key="state_copying_to_tmp_table"),
            "state_end": Metric(MetricType.Integer, key="state_end"),
            "state_freeing_items": Metric(MetricType.Integer, key="state_freeing_items"),
            "state_init": Metric(MetricType.Integer, key="state_init"),
            "state_locked": Metric(MetricType.Integer, key="state_locked"),
            "state_login": Metric(MetricType.Integer, key="state_login"),
            "state_preparing": Metric(MetricType.Integer, key="state_preparing"),
            "state_reading_from_net": Metric(MetricType.Integer, key="state_reading_from_net"),
            "state_sending_data": Metric(MetricType.Integer, key="state_sending_data"),
            "state_sorting_result": Metric(MetricType.Integer, key="state_sorting_result"),
            "state_statistics": Metric(MetricType.Integer, key="state_statistics"),
            "state_updating": Metric(MetricType.Integer, key="state_updating"),
            "state_writing_to_net": Metric(MetricType.Integer, key="state_writing_to_net"),
            "state_none": Metric(MetricType.Integer, key="state_none"),
            "state_other": Metric(MetricType.Integer, key="state_other"),
            "handler_commit": Metric(MetricType.Integer, key="handler_commit"),
            "handler_delete": Metric(MetricType.Integer, key="handler_delete"),
            "handler_discover": Metric(MetricType.Integer, key="handler_discover"),
            "handler_prepare": Metric(MetricType.Integer, key="handler_prepare"),
            "handler_read_first": Metric(MetricType.Integer, key="handler_read_first"),
            "handler_read_key": Metric(MetricType.Integer, key="handler_read_key"),
            "handler_read_next": Metric(MetricType.Integer, key="handler_read_next"),
            "handler_read_prev": Metric(MetricType.Integer, key="handler_read_prev"),
            "handler_read_rnd": Metric(MetricType.Integer, key="handler_read_rnd"),
            "handler_read_rnd_next": Metric(MetricType.Integer, key="handler_read_rnd_next"),
            "handler_rollback": Metric(MetricType.Integer, key="handler_rollback"),
            "handler_savepoint": Metric(MetricType.Integer, key="handler_savepoint"),
            "handler_savepoint_rollback": Metric(MetricType.Integer, key="handler_savepoint_rollback"),
            "handler_update": Metric(MetricType.Integer, key="handler_update"),
            "handler_write": Metric(MetricType.Integer, key="handler_write"),
            "innodb_tables_in_use": Metric(MetricType.Integer, key="innodb_tables_in_use"),
            "innodb_lock_wait_secs": Metric(MetricType.Integer, key="innodb_lock_wait_secs"),
            "hash_index_cells_total": Metric(MetricType.Integer, key="hash_index_cells_total"),
            "hash_index_cells_used": Metric(MetricType.Integer, key="hash_index_cells_used"),
            "total_mem_alloc": Metric(MetricType.Integer, key="total_mem_alloc"),
            "additional_pool_alloc": Metric(MetricType.Integer, key="additional_pool_alloc"),
            "uncheckpointed_bytes": Metric(MetricType.Integer, key="uncheckpointed_bytes"),
            "ibuf_used_cells": Metric(MetricType.Integer, key="ibuf_used_cells"),
            "ibuf_free_cells": Metric(MetricType.Integer, key="ibuf_free_cells"),
            "ibuf_cell_count": Metric(MetricType.Integer, key="ibuf_cell_count"),
            "dictionary_mem_alloc": Metric(MetricType.Integer, key="dictionary_mem_alloc"),
            "innodb_sem_waits": Metric(MetricType.Integer, key="innodb_sem_waits"),
            "innodb_sem_wait_time_ms": Metric(MetricType.Integer, key="innodb_sem_wait_time_ms"),
            "key_buf_bytes_unflushed": Metric(MetricType.Integer, key="key_buf_bytes_unflushed"),
            "key_buf_bytes_used": Metric(MetricType.Integer, key="key_buf_bytes_used"),
            "key_buffer_size": Metric(MetricType.Integer, key="key_buffer_size"),
            "innodb_row_lock_time": Metric(MetricType.Integer, key="innodb_row_lock_time"),
            "innodb_row_lock_waits": Metric(MetricType.Integer, key="innodb_row_lock_waits"),
            "query_time_count_00": Metric(MetricType.Integer, key="query_time_count_00"),
            "query_time_count_01": Metric(MetricType.Integer, key="query_time_count_01"),
            "query_time_count_02": Metric(MetricType.Integer, key="query_time_count_02"),
            "query_time_count_03": Metric(MetricType.Integer, key="query_time_count_03"),
            "query_time_count_04": Metric(MetricType.Integer, key="query_time_count_04"),
            "query_time_count_05": Metric(MetricType.Integer, key="query_time_count_05"),
            "query_time_count_06": Metric(MetricType.Integer, key="query_time_count_06"),
            "query_time_count_07": Metric(MetricType.Integer, key="query_time_count_07"),
            "query_time_count_08": Metric(MetricType.Integer, key="query_time_count_08"),
            "query_time_count_09": Metric(MetricType.Integer, key="query_time_count_09"),
            "query_time_count_10": Metric(MetricType.Integer, key="query_time_count_10"),
            "query_time_count_11": Metric(MetricType.Integer, key="query_time_count_11"),
            "query_time_count_12": Metric(MetricType.Integer, key="query_time_count_12"),
            "query_time_count_13": Metric(MetricType.Integer, key="query_time_count_13"),
            "query_time_total_00": Metric(MetricType.Integer, key="query_time_total_00"),
            "query_time_total_01": Metric(MetricType.Integer, key="query_time_total_01"),
            "query_time_total_02": Metric(MetricType.Integer, key="query_time_total_02"),
            "query_time_total_03": Metric(MetricType.Integer, key="query_time_total_03"),
            "query_time_total_04": Metric(MetricType.Integer, key="query_time_total_04"),
            "query_time_total_05": Metric(MetricType.Integer, key="query_time_total_05"),
            "query_time_total_06": Metric(MetricType.Integer, key="query_time_total_06"),
            "query_time_total_07": Metric(MetricType.Integer, key="query_time_total_07"),
            "query_time_total_08": Metric(MetricType.Integer, key="query_time_total_08"),
            "query_time_total_09": Metric(MetricType.Integer, key="query_time_total_09"),
            "query_time_total_10": Metric(MetricType.Integer, key="query_time_total_10"),
            "query_time_total_11": Metric(MetricType.Integer, key="query_time_total_11"),
            "query_time_total_12": Metric(MetricType.Integer, key="query_time_total_12"),
            "query_time_total_13": Metric(MetricType.Integer, key="query_time_total_13"),
            "wsrep_replicated_bytes": Metric(MetricType.Integer, key="wsrep_replicated_bytes"),
            "wsrep_received_bytes": Metric(MetricType.Integer, key="wsrep_received_bytes"),
            "wsrep_replicated": Metric(MetricType.Integer, key="wsrep_replicated"),
            "wsrep_received": Metric(MetricType.Integer, key="wsrep_received"),
            "wsrep_local_cert_failures": Metric(MetricType.Integer, key="wsrep_local_cert_failures"),
            "wsrep_local_bf_aborts": Metric(MetricType.Integer, key="wsrep_local_bf_aborts"),
            "wsrep_local_send_queue": Metric(MetricType.Integer, key="wsrep_local_send_queue"),
            "wsrep_local_recv_queue": Metric(MetricType.Integer, key="wsrep_local_recv_queue"),
            "wsrep_cluster_size": Metric(MetricType.Integer, key="wsrep_cluster_size"),
            "wsrep_cert_deps_distance": Metric(MetricType.Integer, key="wsrep_cert_deps_distance"),
            "wsrep_apply_window": Metric(MetricType.Integer, key="wsrep_apply_window"),
            "wsrep_commit_window": Metric(MetricType.Integer, key="wsrep_commit_window"),
            "wsrep_flow_control_paused": Metric(MetricType.Integer, key="wsrep_flow_control_paused"),
            "wsrep_flow_control_sent": Metric(MetricType.Integer, key="wsrep_flow_control_sent"),
            "wsrep_flow_control_recv": Metric(MetricType.Integer, key="wsrep_flow_control_recv"),
            "pool_reads": Metric(MetricType.Integer, key="pool_reads"),
            "pool_read_requests": Metric(MetricType.Integer, key="pool_read_requests"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        key = metric.kwargs.get("key")
        try:
            return self._correct_type(metric.type, self.test_data[key])
        except KeyError:
            return 0

    def _load_data(self):
        self.test_data = Cache.read(self.name)
        if self.test_data is not None:
            return

        self._init_connector()

        self.test_data = {}
        self._get_global_status()
        self._get_variables()

        if self.config.get("check_slave", True):
            self._get_slave_status()

        if self.config.get("check_master", True) and dict_has_item(self.test_data, "log_bin", "ON"):
            self._get_master_status()

        if self.config.get("check_procs", True):
            self._get_processlist()

        if self.config.get("check_innodb", True) and dict_has_item(self.test_data, "have_innodb", "YES"):
            self._get_innodb_status()

        # Not yet implemented
        # if self.config.get("check_qrt", True):
        # self._get_percona_qrt()

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

        binlog_size = 0
        for log in master_logs:
            log = dict_keys_to_lower(log)
            if "file_size" in log and log["file_size"] > 0:
                binlog_size += int(log["file_size"])

        self.test_data["binary_log_space"] = binlog_size

    def _get_processlist(self):
        states = {
            "state_closing_tables": 0,
            "state_copying_to_tmp_table": 0,
            "state_end": 0,
            "state_freeing_items": 0,
            "state_init": 0,
            "state_locked": 0,
            "state_login": 0,
            "state_preparing": 0,
            "state_reading_from_net": 0,
            "state_sending_data": 0,
            "state_sorting_result": 0,
            "state_statistics": 0,
            "state_updating": 0,
            "state_writing_to_net": 0,
            "state_none": 0,
            "state_other": 0,
        }

        processlist = self.connector.get("SHOW PROCESSLIST")
        for process in processlist:
            state = str(process["State"])

            if "Table lock" in state or "Waiting for" in state:
                state = "locked"

            statekey = "state_%s" % state.lower()
            if statekey in states:
                states[statekey] += 1
            else:
                states["state_other"] += 1

        self.test_data.update(states)

    def _get_innodb_status(self):
        status = {
            "spin_waits": 0,
            "spin_rounds": 0,
            "os_waits": 0,
            "current_transactions": 0,
            "active_transactions": 0,
            "innodb_lock_wait_secs": 0,
            "innodb_tables_in_use": 0,
            "innodb_locked_tables": 0,
            "innodb_lock_structs": 0,
            "locked_transactions": 0,
            "hash_index_cells_used": 0,
            "pool_size": 0,
            "free_pages": 0,
            "database_pages": 0,
            "modified_pages": 0,
            "log_bytes_written": 0,
            "log_bytes_flushed": 0,
            "last_checkpoint": 0,
        }

        innodb_status = self.connector.get("SHOW /*!50000 ENGINE*/ INNODB STATUS")[0]["Status"].split("\n")
        for row in innodb_status:
            column = filter(bool, row.translate(None, ",.:;").split(" "))

            if "Mutex spin waits" in row:
                status["spin_waits"] += int(column[3])
                status["spin_rounds"] += int(column[5])
                status["os_waits"] += int(column[8])
            elif "RW-shared spins" in row:
                status["spin_waits"] += int(column[2])
                status["spin_rounds"] += int(column[4])
                status["os_waits"] += int(column[7])
            elif "RW-excl spins" in row:
                status["spin_waits"] += int(column[2])
                status["spin_rounds"] += int(column[4])
                status["os_waits"] += int(column[7])
            elif "Trx id counter" in row:
                status["innodb_transactions"] = self.get_big_number(column[3])
            elif "Purge done for trx" in row:
                status["unpurged_transactions"] = status["innodb_transactions"] - self.get_big_number(column[6])
            elif "History list length" in row:
                status["history_list"] = int(column[3])
            elif "---TRANSACTION" in row:
                status["current_transactions"] += 1
                if row.endswith("ACTIVE"):
                    status["active_transactions"] += 1
            elif "------- TRX HAS BEEN" in row:
                status["innodb_lock_wait_secs"] += int(column[5])
            elif "read views open inside InnoDB" in row:
                status["read_views"] = int(column[0])
            elif "mysql tables in use" in row:
                status["innodb_tables_in_use"] += int(column[4])
                status["innodb_locked_tables"] += int(column[6])
            elif "lock struct(s)" in row:
                if row.startswith("LOCK WAIT"):
                    status["innodb_lock_structs"] += int(column[2])
                    status["locked_transactions"] += 1
                else:
                    status["innodb_lock_structs"] += int(column[0])
            elif " OS file reads, " in row:
                status["file_reads"] = int(column[0])
                status["file_writes"] = int(column[4])
                status["file_fsyncs"] = int(column[8])
            elif "Pending normal aio reads:" in row:
                status["pending_normal_aio_reads"] = int(column[4])
                status["pending_normal_aio_writes"] = int(column[7])
            elif "ibuf aio reads" in row:
                status["pending_ibuf_aio_reads"] = int(column[3])
                status["pending_aio_log_ios"] = int(column[6])
                status["pending_aio_sync_ios"] = int(column[9])
            elif "Pending flushes (fsync)" in row:
                status["pending_log_flushes"] = int(column[4])
                status["pending_buf_pool_flushes"] = int(column[7])
            elif "Ibuf: size " in row:
                status["ibuf_used_cells"] = int(column[2])
                status["ibuf_free_cells"] = int(column[6])
                status["ibuf_cell_count"] = int(column[9])
            elif " merged recs, " in row:
                status["ibuf_inserts"] = int(column[0])
                status["ibuf_merged"] = int(column[2])
                status["ibuf_merges"] = int(column[5])
            elif "Hash table size " in row:
                status["hash_index_cells_total"] = int(column[3])
                if "used cells" in row:
                    status["hash_index_cells_used"] = int(column[6])
            elif " log i/o's done, " in row:
                status["log_writes"] = int(column[0])
            elif " pending log writes, " in row:
                status["pending_log_writes"] = int(column[0])
                status["pending_chkp_writes"] = int(column[4])
            elif "Log sequence number" in row:
                status["log_bytes_written"] = int(column[3])
            elif "Log flushed up to" in row:
                status["log_bytes_flushed"] = int(column[4])
            elif "Last checkpoint at" in row:
                status["last_checkpoint"] = int(column[3])
            elif "Total memory allocated" in row:
                status["total_mem_alloc"] = int(column[3])
                status["additional_pool_alloc"] = int(column[8])
            elif "Dictionary memory allocated" in row:
                status["dictionary_mem_alloc"] = int(column[3])
            elif "Buffer pool size " in row:
                if status["pool_size"] == 0:
                    status["pool_size"] = int(column[3])
            elif "Free buffers" in row:
                if status["free_pages"] == 0:
                    status["free_pages"] = int(column[2])
            elif "Database pages" in row:
                if status["database_pages"] == 0:
                    status["database_pages"] = int(column[2])
            elif "Modified db pages" in row:
                if status["modified_pages"] == 0:
                    status["modified_pages"] = int(column[3])
            elif "Pages read" in row and "ahead" not in row:
                status["pages_read"] = int(column[2])
                status["pages_created"] = int(column[4])
                status["pages_written"] = int(column[6])
            elif "Number of rows inserted" in row:
                status["rows_inserted"] = int(column[4])
                status["rows_updated"] = int(column[6])
                status["rows_deleted"] = int(column[8])
                status["rows_read"] = int(column[10])
            elif " queries inside InnoDB, " in row:
                status["queries_inside"] = int(column[0])
                status["queries_queued"] = int(column[4])

        status["unflushed_log"] = status["log_bytes_written"] - status["log_bytes_flushed"]
        status["uncheckpointed_bytes"] = status["log_bytes_written"] - status["last_checkpoint"]

        self.test_data.update(status)

    def _get_percona_qrt(self):
        percona_qrt = self.connector.get("SELECT `count`, total * 1000000 AS total "
                                         "FROM INFORMATION_SCHEMA.QUERY_RESPONSE_TIME WHERE `time` <> 'TOO LONG'")

    def _format_data(self, data, key_column="Variable_name", value_column="Value"):
        tmp = {}
        for value in data:
            tmp[value[key_column].lower()] = value[value_column]

        return tmp

    def get_big_number(self, hi, lo=None):
        if hi is None or len(hi) < 1:
            return 0

        if lo is None or len(lo) < 1:
            return int(hi, 16)

        return (hi * 4294967296) + lo