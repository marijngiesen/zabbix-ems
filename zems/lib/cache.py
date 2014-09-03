# This class writes collected monitoring data to a temporary file
class Cache:
    def __init__(self):
        pass

    @staticmethod
    def write(id, data):
        with open("/tmp/zems-%s" % id, "w") as tmpfile:
            tmpfile.writelines(data)

    @staticmethod
    def read(id):
        with open("/tmp/zems-%s" % id, "r") as tmpfile:
            return tmpfile.readlines()