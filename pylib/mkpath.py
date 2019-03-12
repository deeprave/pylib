# -*- coding: utf-8 -*-
import errno
import logging
import os
import sys


def mkpath(path, mode=0o755):
    try:
        os.makedirs(path, mode)
        logging.debug("Created folder: {}".format(path))
    except (OSError, IOError):
        exc = sys.exc_info()
        if exc[1].errno != errno.EEXIST:
            raise
