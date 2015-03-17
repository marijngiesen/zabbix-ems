import os

from check import Check, CheckFail, MetricType, Metric
from lib import utils
from lib.cache import Cache


class RdiffBackup(Check):
    name = "rdiff-backup"

    def _init_metrics(self):
        self.metrics = {
            "start_time": Metric("StartTime", MetricType.Float, 0, " "),
            "end_time": Metric("EndTime", MetricType.Float, 1, " "),
            "elapsed_time": Metric("ElapsedTime", MetricType.Float, 2, " "),
            "source_files": Metric("SourceFiles", MetricType.Integer, 3, " "),
            "source_file_size": Metric("SourceFileSize", MetricType.Integer, 4, " "),
            "mirror_files": Metric("MirrorFiles", MetricType.Integer, 5, " "),
            "mirror_file_size": Metric("MirrorFileSize", MetricType.Integer, 6, " "),
            "new_files": Metric("NewFiles", MetricType.Integer, 7, " "),
            "new_file_size": Metric("NewFileSize", MetricType.Integer, 8, " "),
            "deleted_files": Metric("DeletedFiles", MetricType.Integer, 9, " "),
            "deleted_file_size": Metric("DeletedFileSize", MetricType.Integer, 10, " "),
            "changed_files": Metric("ChangedFiles", MetricType.Integer, 11, " "),
            "changed_source_size": Metric("ChangedSourceSize", MetricType.Integer, 12, " "),
            "changed_mirror_size": Metric("ChangedMirrorSize", MetricType.Integer, 13, " "),
            "increment_files": Metric("IncrementFiles", MetricType.Integer, 14, " "),
            "increment_file_size": Metric("IncrementFileSize", MetricType.Integer, 15, " "),
            "total_dest_size_change": Metric("TotalDestinationSizeChange", MetricType.Integer, 16, " "),
            "errors": Metric("Errors", MetricType.Integer, 17, " "),
        }

    def _get(self, metric=None, *args, **kwargs):
        self.test_data = self._load_data()
        return self._get_value(self.metrics[metric])

    def _get_value(self, metric):
        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        self.test_data = Cache.read(self.name, 3000)
        if self.test_data is not None:
            return self.test_data

        with open(self._get_statistics_file(), "r") as f:
            self.test_data = f.readlines()

        Cache.write(self.name, self.test_data)

        return self.test_data

    def _get_statistics_file(self):
        files = utils.find_files(
            os.path.join(self.config.get("rdiff_backup_path", "/mnt/backup/system"), "rdiff-backup-data"),
            "session_statistics")
        return utils.determine_newest_file(files)


