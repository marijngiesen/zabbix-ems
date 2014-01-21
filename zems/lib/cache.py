# This class writes collected monitoring data to a temporary file

class Cache:
	def __init__(self):
		pass

	def write(self, id, data):
		with open("/tmp/zems-%s" % id, "w") as tmpfile:
			tmpfile.writelines(data)
