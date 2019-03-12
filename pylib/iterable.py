# -*- coding: utf-8 -*-
"""
    This module implements a function to test if a value is "iterable",
    specifically excluding None, str, bytes or any variation thereof,
    but includes dict, generators and other iterator interface providers.

    is_iterable(value) - test if a value is iterable
    iterable(value) - converts a value into an iterable, if it isn't ready one.
            None - returns an empty list
            non-iterable - returns the value wrapped in a list
            iterable - returns the value unchanged
"""
import six
from .pyver import PY36, byte_types
if PY36:
    from collections.abc import Iterable
else:
    from collections import Iterable

__all__ = (
    'is_iterable',
    'iterable',
)

string_types = six.string_types + byte_types


def is_iterable(value, not_dict=False):
    """
    Determine if a value is iterable ignoring char seq and optionally dict

    :param value: value to test
    :param not_dict: if true, passing a dict will return false
    :return: whether the value is iterable or not
    """
    # type: (object, bool)
    return value is not None and isinstance(value, Iterable) and \
        not (not_dict and isinstance(value, dict)) and \
        not isinstance(value, string_types)


def iterable(value, not_dict=False):
    """
    Make a non-iterable value iterable

    :param value: any iterable or non-iterable
    :param not_dict: set true to consider a dict non-iterable
    :return: iterable value
    """
    # type: (object, bool)
    return list() if value is None else value if is_iterable(value, not_dict) else [value]
