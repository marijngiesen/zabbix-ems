import os

from check import Check, CheckFail, MetricType, Metric
from lib import utils
from lib.cache import Cache


class RdiffBackup(Check):
    name = "rdiff-backup"

    def _init_metrics(self):
        self.metrics = {
            "start_time": Metric(MetricType.Float, regex="StartTime ([0-9\.]+)"),
            "end_time": Metric(MetricType.Float, regex="EndTime ([0-9\.]+)"),
            "elapsed_time": Metric(MetricType.Float, regex="ElapsedTime ([0-9\.]+)"),
            "source_files": Metric(MetricType.Integer, regex="SourceFiles ([0-9]+)"),
            "source_file_size": Metric(MetricType.Integer, regex="SourceFileSize ([0-9]+)"),
            "mirror_files": Metric(MetricType.Integer, regex="MirrorFiles ([0-9]+)"),
            "mirror_file_size": Metric(MetricType.Integer, regex="MirrorFileSize ([0-9]+)"),
            "new_files": Metric(MetricType.Integer, regex="NewFiles ([0-9]+)"),
            "new_file_size": Metric(MetricType.Integer, regex="NewFileSize ([0-9]+)"),
            "deleted_files": Metric(MetricType.Integer, regex="DeletedFiles ([0-9]+)"),
            "deleted_file_size": Metric(MetricType.Integer, regex="DeletedFileSize ([0-9]+)"),
            "changed_files": Metric(MetricType.Integer, regex="ChangedFiles ([0-9]+)"),
            "changed_source_size": Metric(MetricType.Integer, regex="ChangedSourceSize ([0-9]+)"),
            "changed_mirror_size": Metric(MetricType.Integer, regex="ChangedMirrorSize ([0-9]+)"),
            "increment_files": Metric(MetricType.Integer, regex="IncrementFiles ([0-9]+)"),
            "increment_file_size": Metric(MetricType.Integer, regex="IncrementFileSize ([0-9]+)"),
            "total_dest_size_change": Metric(MetricType.Integer, regex="TotalDestinationSizeChange ([0-9]+)"),
            "errors": Metric(MetricType.Integer, regex="Errors ([0-9]+)"),
        }

    def _get(self, metric=None, *args, **kwargs):
        self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        return self._correct_type(metric.type, metric.parser.get_value(self.test_data))

    def _load_data(self):
        self.test_data = Cache.read(self.name, ttl=3600)
        if self.test_data is not None:
            return

        with open(self._get_statistics_file(), "r") as f:
            self.test_data = "".join(f.readlines())

        Cache.write(self.name, self.test_data)

        return self.test_data

    def _get_statistics_file(self):
        files = utils.find_files(
            os.path.join(self.config.get("rdiff_backup_path", "/mnt/backup/system"), "rdiff-backup-data"),
            "session_statistics")
        return utils.determine_newest_file(files)


