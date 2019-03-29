# -*- coding: utf-8 -*-
"""
Implement a simple function timer
"""
from types import FunctionType
import datetime


def timer(func, *args, **kwargs):
    """

    :param any func: function to call
    :param args: ...
    :param kwargs: ...
    :return: (return value(s), duration)
    """
    start = datetime.datetime.now()
    value = func(*args, **kwargs)
    end = datetime.datetime.now()
    return value, end.replace(microsecond=0) - start.replace(microsecond=0)
