# -*- coding: utf-8 -*-
import sys

__all__ = (
    'PY2',
    'PY3',
    'PY36',
    'byte_types',
    'is_unicode',
    'from_unicode'
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
    return isinstance(value, unicode) if PY2 else False


def from_unicode(value):
    return value.encode('utf-8') if is_unicode(value) else value
