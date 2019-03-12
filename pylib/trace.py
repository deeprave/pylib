# -*- coding: utf-8 -*-
# dynamically add TRACE logging level
import logging
import os
from types import MethodType


# define the new level
logging.TRACE = 5

# fixup name<->value translation
# noinspection PyUnresolvedReferences
logging.addLevelName(logging.TRACE, 'TRACE')


# add define and add the trace method to Logger
# noinspection PyUnresolvedReferences
def trace_method(self, msg, *args, **kwargs):
    if self.isEnabledFor(logging.TRACE):
        self._log(logging.TRACE, msg, args, **kwargs)


logging.Logger.trace = MethodType(trace_method, logging.Logger)


# add and define the trace method to the root logger
def trace_logger(msg, *args, **kwargs):
    # noinspection PyUnresolvedReferences
    logging.log(logging.TRACE, msg, *args, **kwargs)


logging.trace = trace_logger


# noinspection PyUnresolvedReferences
levels = (
    logging.FATAL,
    logging.CRITICAL, 
    logging.ERROR, 
    logging.WARNING, 
    logging.INFO, 
    logging.DEBUG,
    logging.TRACE,
)


# noinspection PyProtectedMember
def to_level(value):
    """ convert an integer or string to logging level value """
    if str.isdigit(str(value)):
        value = int(value)
        if value < 0:
            return logging.NOTSET
        elif value >= len(levels):
            value = len(levels) - 1
        value = levels[value]
    elif value:
        value = value.upper()
        if hasattr(logging, '_nameToLevel'):
            if value not in logging._nameToLevel:   # noqa PY3
                raise KeyError("'{}' is not a valid log level".format(value))
            value = logging._nameToLevel[value]     # noqa
        else:
            if value not in logging._levelNames:    # PY2
                raise KeyError("'{}' is not a valid log level".format(value))
            value = logging._levelNames[value]
    return value


# noinspection PyPep8Naming
def setup_logging(log_name=None, log_path=None, format=None,
                  log_level=logging.INFO, console_level=None, file_level=None):
    """ set up basic logging, optionally adding a logfile handler """
    console_level = log_level if console_level is None else console_level
    file_level = log_level if file_level is None else file_level
    rootLogger = logging.getLogger()
    logFormatter = logging.Formatter('%(asctime)s %(levelname)8s %(message)s' if format is None else format)
    if log_name is not None:
        logPath = log_name if log_path is None else os.path.join(log_path, log_name)
        fileHandler = logging.FileHandler(logPath)
        fileHandler.setFormatter(logFormatter)
        fileHandler.setLevel(file_level)
        rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(console_level)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(log_level)
