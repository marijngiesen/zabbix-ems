try:
    import MySQLdb
except ImportError:
    import sys
    MySQLdb = None
    print "Error: MySQL-python module cannot be loaded"
    sys.exit(1)


class MySQLConnector:
    socket_file = None
    host = None
    port = None
    user = None
    passwd = None
    db = None
    connection = None

    def __init__(self, socket_file=None, host=None, port=None, user="", passwd="", db=""):
        self.socket_file = socket_file
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.db = db

    def get(self, query):
        return self._read(query)

    def _connect(self):
        if self.connection is not None:
            return

        if self.socket_file is not None:
            self.connection = MySQLdb.connect(unix_socket=self.socket_file, user=self.user, passwd=self.passwd,
                                              db=self.db)
        else:
            self.connection = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,
                                              db=self.db)

        self.connection.autocommit(True)

    def _read(self, query):
        self._connect()
        cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(query)
        items = cursor.fetchall()
        cursor.close()

        return items
