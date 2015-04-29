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
import json
import traceback
import ConfigParser

try:
    from enum import Enum
except ImportError:
    Enum = None
    print "Error: enum34 module cannot be loaded, please install using 'pip install enum34'"
    sys.exit(1)

from lib.parser import Parser
from lib.logger import Logger


class Check(object):
    name = "zems"
    config = None
    debug = False
    logger = None
    confdir = "/etc/zems"

    metrics = None
    test_data = None
    default_value = {}

    def __init__(self, name=None):
        if name is not None:
            self.name = name
        if self.name == 'zems':
            raise NotImplementedError("Class %s must redefine its name" % (self.__class__.__name__, ))

        self.config = self._get_config()

        if self.config.get('debug', False):
            self.debug = True

        self.logger = Logger.get(self.__class__.__name__, self.config.get("logfile", Logger.logfile), self.debug)
        self.logger.debug("config file: %s" % os.path.join(self.confdir, self.name + ".conf"))

        self.default_value = {
            MetricType.Integer: 0,
            MetricType.Float: 0.0,
            MetricType.String: "",
            MetricType.Discovery: []
        }

        self._init_metrics()

    def _init_metrics(self):
        raise NotImplementedError("Class %s must reimplement _init_metrics method"
                                  % (self.__class__.__name__, ))

    def _get(self, *args, **kwargs):
        raise NotImplementedError("Class %s must reimplement _get method"
                                  % (self.__class__.__name__, ))

    def get(self, metric=None, *args, **kwargs):
        self.logger.debug("executed get metric '%s', args '%s', kwargs '%s'" %
                          (str(metric), str(args), str(kwargs)))
        try:
            metric = metric.lower()
            if metric not in self.metrics:
                raise CheckFail("Requested unknown metric: %s" % metric)

            print self._get(metric, *args, **kwargs)
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

    def _correct_type(self, metric_type, value):
        try:
            if metric_type == MetricType.String:
                return str(value.strip())
            elif metric_type == MetricType.Float:
                return float(value)
            elif metric_type == MetricType.Integer:
                return int(value)
            elif metric_type == MetricType.Discovery:
                return self._to_discovery_output(value)
            else:
                raise CheckFail("Unknown return type")
        except TypeError:
            return self.default_value[metric_type]
        except ValueError:
            return self.default_value[metric_type]

    def _get_config(self):
        config = MyConfigParser()
        config.read(os.path.join(self.confdir, self.name + ".conf"))
        return config

    def _to_discovery_output(self, data):
        return json.dumps({"data": data})


class MetricType(Enum):
    Integer = 0
    Float = 1
    String = 2
    Discovery = 3


class Metric(object):
    type = None
    parser = None
    callback = None
    kwargs = {}

    def __init__(self, metric_type, callback=None, regex=None, position=None, linenumber=None, separator=None,
                 **kwargs):
        self.type = metric_type
        self.kwargs = kwargs

        if metric_type == MetricType.Discovery and callback is None:
            raise ValueError(
                "Type of metric is discovery, but no callback specified. Discovery metrics always need a callback.")

        if callback is not None:
            self.callback = callback

        self.parser = Parser(regex=regex, position=position, linenumber=linenumber, separator=separator)


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