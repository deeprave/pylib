# -*- coding: utf-8 -*-
import sys

__all__ = (
    'PY2',
    'PY3',
    'PY36',
    'byte_types',
    'is_unicode',
    'from_unicode',
    'to_unicode',
)


PY2 = (sys.version_info[0] == 2)
PY3 = (sys.version_info[0] >= 3)
PY36 = (sys.version_info[0] > 3 or (sys.version_info[0] == 3 and sys.version_info[1] >= 6))

if PY3:
    # noinspection PyShadowingBuiltins
    unicode = str
    byte_types = (bytes, bytearray)

else:
    byte_types = (str,)


def is_unicode(value):
    return isinstance(value, unicode)


def from_unicode(value, encoding='utf-8'):
    if not is_unicode(value):
        return value
    return value.decode(encoding)


def to_unicode(value, encoding='utf-8'):
    if is_unicode(value):
        return value
    return value.decode(encoding)
