#!/usr/bin/env python
"""
    ZTCCheck class - wrapper for ztc checks
    provides logging, output formatting and error handling abilities

    This file is part of ZTC and distributed under same license.

    Copyright (c) 2011 Denis Seleznyov [https://bitbucket.org/xy2/]
    Copyright (c) 2011 Vladimir Rusinov <vladimir@greenmice.info>
    Copyright (c) 2011 Murano Software [http://muranosoft.com]

    Modified for use in Zabbix EMS by Marijn Giesen <marijn@studio-donder.nl>
"""
import os
import sys
import logging
import logging.handlers
import traceback
import ConfigParser
from enum import Enum


class Check(object):
    name = "zems"
    config = None
    debug = False
    logger = None
    confdir = "config"

    metrics = None
    test_data = None
    test_data_filtered = None

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        if self.name == 'zems':
            raise NotImplementedError("Class %s must redefine its name" % (self.__class__.__name__, ))

        self.config = self._get_config()

        if self.config.get('debug', False):
            self.debug = True

        self.logger = logging.getLogger(self.__class__.__name__)
        self._set_logger_options()

        self.logger.debug("config file: %s" % os.path.join(self.confdir, self.name + ".conf"))

        self._init_metrics()

    def _init_metrics(self):
        raise NotImplementedError("Class %s must reimplement _init_metrics method"
                                  % (self.__class__.__name__, ))

    def _get(self, *args, **kwargs):
        raise NotImplementedError("Class %s must reimplement _get method"
                                  % (self.__class__.__name__, ))

    def get_val(self, metric=None, *args, **kwargs):
        ret = self._get(metric, *args, **kwargs)
        if type(ret) == float:
            # prevent from printing in exp form
            ret = ("%.6f" % ret).rstrip('0').rstrip('.')
        return ret

    def get(self, metric=None, *args, **kwargs):
        self.logger.debug("executed get metric '%s', args '%s', kwargs '%s'" %
                          (str(metric), str(args), str(kwargs)))
        try:
            print self.get_val(metric, *args, **kwargs)
        except CheckFail, e:
            self.logger.exception('Check fail, getting %s' % (metric, ))
            if self.debug:
                traceback.print_stack()
            for arg in e.args:
                print(arg)
            sys.exit(1)
        except CheckTimeout, e:
            self.logger.exception('Check timeout, getting %s' % (metric, ))
            if self.debug:
                traceback.print_stack()
            for arg in e.args:
                print(arg)
            sys.exit(2)
        except Exception, e:
            self.logger.exception('Check unexpected error, getting %s' % (metric, ))
            sys.exit(1)

    def print_metrics(self):
        print "Available metrics:"
        for metric in sorted(self.metrics.keys()):
            print "  %s" % metric

    def need_root(self):
        if os.getuid() != 0:
            self.logger.exception("Need root privileges to perform this check")
            sys.exit(1)

    def _correct_type(self, type, value):
        if type == MetricType.String:
            return str(value).strip()
        elif type == MetricType.Float:
            if len(value) == 0:
                return 0
            return float(value)
        elif type == MetricType.Integer:
            if len(value) == 0:
                return 0
            return int(value)
        else:
            raise CheckFail("Unknown return type")

    def _get_config(self):
        config = MyConfigParser()
        config.read(os.path.join(self.confdir, self.name + ".conf"))
        return config

    def _set_logger_options(self):
        formatter = logging.Formatter("[%(name)s] %(asctime)s - %(levelname)s: %(message)s")

        # setting file handler (max 10 files of 1MB)
        h = logging.handlers.RotatingFileHandler(self.config.get("logfile", "/var/log/zems.log"), "a", 1 * 1024 * 1024, 10)

        if self.debug:
            # setting stream handler
            sh = logging.StreamHandler()
            sh.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
            sh.setFormatter(formatter)
            h.setLevel(logging.DEBUG)
            self.logger.addHandler(sh)
        else:
            self.logger.setLevel(logging.WARN)
            h.setLevel(logging.WARN)

        h.setFormatter(formatter)
        self.logger.addHandler(h)
        self.logger.debug("created")


class MetricType(Enum):
    Integer = 0
    Float = 1
    String = 2


class Metric(object):
    key = None
    position = None
    type = None
    separator = None
    filter_callback = None
    kwargs = {}

    def __init__(self, key, position, type, separator, filter_callback=None, **kwargs):
        self.key = key
        self.position = position
        self.type = type
        self.separator = separator
        self.filter_callback = filter_callback
        self.kwargs = kwargs

    def __repr__(self):
        return self.key


class MyConfigParser(ConfigParser.ConfigParser):
    def __init__(self, section='main'):
        self.sectname = section
        ConfigParser.ConfigParser.__init__(self)

    def get(self, option, default):
        try:
            return ConfigParser.ConfigParser.get(self, self.sectname, option)
        except Exception, e:
            return default


class CheckFail(Exception):
    pass


class CheckTimeout(Exception):
    pass