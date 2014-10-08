import os
from commandr import command

from check import Check, CheckFail, MetricType, Metric
from lib import utils


class RdiffBackup(Check):
    name = "rdiff-backup"

    def _init_metrics(self):
        self.metrics = {
            "elapsed_time": Metric("ElapsedTime", 2, MetricType.Float, " "),
            "source_files": Metric("SourceFiles", 3, MetricType.Integer, " "),
            "source_file_size": Metric("SourceFileSize", 4, MetricType.Integer, " "),
            "mirror_files": Metric("MirrorFiles", 5, MetricType.Integer, " "),
            "mirror_file_size": Metric("MirrorFileSize", 6, MetricType.Integer, " "),
            "new_files": Metric("NewFiles", 7, MetricType.Integer, " "),
            "new_file_size": Metric("NewFileSize", 8, MetricType.Integer, " "),
            "deleted_files": Metric("DeletedFiles", 9, MetricType.Integer, " "),
            "deleted_file_size": Metric("DeletedFileSize", 10, MetricType.Integer, " "),
            "changed_files": Metric("ChangedFiles", 11, MetricType.Integer, " "),
            "changed_source_size": Metric("ChangedSourceSize", 12, MetricType.Integer, " "),
            "changed_mirror_size": Metric("ChangedMirrorSize", 13, MetricType.Integer, " "),
            "increment_files": Metric("IncrementFiles", 14, MetricType.Integer, " "),
            "increment_file_size": Metric("IncrementFileSize", 15, MetricType.Integer, " "),
            "total_dest_size_change": Metric("TotalDestinationSizeChange", 16, MetricType.Integer, " "),
            "errors": Metric("Errors", 17, MetricType.Integer, " "),
        }

    def _get(self, metric=None, *args, **kwargs):
        metric = metric.lower()
        if metric in self.metrics:
            self.test_data = self._load_data()
            return self._get_value(self.metrics[metric])

        raise CheckFail("Requested not allowed metric")

    def _get_value(self, metric):
        return self._correct_type(metric.type, self.test_data[metric.position].split(metric.separator)[1])

    def _load_data(self):
        if self.test_data is None:
            with open(self._get_statistics_file(), "r") as f:
                self.test_data = f.readlines()

        return self.test_data

    def _get_statistics_file(self):
        files = utils.find_files(
            os.path.join(self.config.get("rdiff_backup_path", "/mnt/backup/system"), "rdiff-backup-data"),
            "session_statistics")
        return utils.determine_newest_file(files)


@command("rdiff-backup")
def rdiffbackup(key=None):
    test = RdiffBackup()

    if key is not None:
        test.need_root()
        test.get(key)
    else:
        test.print_metrics()