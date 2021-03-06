import os
from datetime import datetime
from subprocess import Popen, STDOUT, PIPE

from logger import Logger


def find_files_by_extension(path, extension):
    if not extension.startswith("."):
        extension = "." + extension

    files = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk(path)
        for filename in files if filename.endswith(extension)
        ]

    if len(files) < 1:
        raise IOError("No files found with extension %s" % extension)

    return files


def find_files(path, name):
    files = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk(path)
        for filename in files if name in filename
        ]

    if len(files) < 1:
        raise IOError("No files found with name %s" % name)

    return files


def determine_newest_file(files):
    modified_at = 0
    newest_file = None

    for filename in files:
        tmp = os.path.getmtime(filename)
        if tmp > modified_at:
            modified_at = tmp
            newest_file = filename

    return newest_file


def run_command(command):
    process = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    output, error = process.communicate()
    returncode = process.poll()

    if returncode != 0:
        raise RuntimeError("Error running command '%s': %s (%s)" % (command, error, returncode))

    return output


def transpose_dict(data, key):
    if type(data) is not list:
        return None

    tmp = {}
    for row in data:
        if key not in row:
            return None

        tmp[row[key]] = row

    return tmp


def dict_has_item(data, key, value):
    if type(data) is not dict:
        return False

    if key not in data:
        return False

    if data[key] != value:
        return False

    return True


def dict_keys_to_lower(data):
    if type(data) is not dict:
        return None

    return dict((k.lower(), v) for k, v in data.iteritems())


def log_performance(func):
    def wrapper(*args, **kwargs):
        if not Logger.debug:
            return func(*args, **kwargs)

        t1 = datetime.now()
        res = func(*args, **kwargs)
        t2 = datetime.now() - t1

        if args[0].logger is not None:
            args[0].logger.debug(
                "Performance: Executed method %s in %d.%06ds" % (func.__name__, t2.seconds, t2.microseconds))
        else:
            logger = Logger.get("Performance")
            logger.debug("Executed method %s in %ss" % (func.__name__, str(t2)))

        return res

    return wrapper
