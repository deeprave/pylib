# -*- coding: utf-8 -*-
import errno
import logging
import os
import sys


def mkpath(path, mode=0o755, log_create=False):
    if path:
        try:
            os.makedirs(path, mode)
            if log_create:
                logging.debug("Created folder: {}".format(path))
        except (OSError, IOError):
            exc = sys.exc_info()
            if exc[1].errno != errno.EEXIST:
                raise
