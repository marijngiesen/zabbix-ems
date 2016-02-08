import logging
import logging.handlers


class Logger(object):
    # Default logfile
    logfile = "/var/log/zems.log"
    debug = False

    @staticmethod
    def get(name, logfile=None, debug=None):
        if logfile is None:
            logfile = Logger.logfile
        else:
            Logger.logfile = logfile

        if debug is None:
            debug = Logger.debug
        else:
            Logger.debug = debug

        logger = logging.getLogger(name)
        return Logger._init(logger, logfile, debug)

    @staticmethod
    def _init(logger, logfile, debug):
        formatter = logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s: %(message)s")

        h = logging.StreamHandler(open(logfile, "a"))

        if debug:
            # setting stream handler
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            h.setLevel(logging.DEBUG)
            logger.addHandler(sh)
        else:
            logger.setLevel(logging.WARN)
            h.setLevel(logging.WARN)

        h.setFormatter(formatter)
        logger.addHandler(h)
        logger.debug("Loghandler created")

        return logger
