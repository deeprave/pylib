# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Iterable

from six import binary_type, integer_types, string_types, text_type

from .odict import odict

__all__ = ('serialize_obj',)

PRIMATIVES = string_types + integer_types + (text_type,) + (binary_type,) + (float, bool,)


def serialize_obj(obj, empty_ok=False):
    # type: (object, bool) -> object

    def allow_empty(o):
        if not empty_ok:
            if o is None:
                return False
            # primitives, always allow
            if isinstance(o, PRIMATIVES):
                return True
            if not o:
                return False
        return True

    result = odict()
    if isinstance(obj, (list, tuple, set)):
        return [serialize_obj(mem) for mem in obj if allow_empty(mem)]
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if allow_empty(v):
                r = serialize_obj(v, empty_ok=empty_ok)
                if allow_empty(r):
                    result[k] = r
    elif hasattr(obj, '__dict__')and obj.__dict__:
        for k, v in obj.__dict__.items():
            if not callable(v) and allow_empty(v):
                r = serialize_obj(v, empty_ok=empty_ok)
                if allow_empty(r):
                    result[k] = r
    elif hasattr(obj, '__iter__') and isinstance(obj, Iterable):
        for k, v in obj:
            if allow_empty(v):
                r = serialize_obj(v, empty_ok=empty_ok)
                if allow_empty(r):
                    result[k] = r
    elif hasattr(obj, '__slots__') and obj.__slots__:
        for k in obj.__slots__:
            try:
                v = getattr(obj, k)
                if allow_empty(v):
                    r = serialize_obj(v, empty_ok=empty_ok)
                    if allow_empty(r):
                        result[k] = r
            except AttributeError:
                result = str(obj)
                break
    elif isinstance(obj, datetime):
        result = obj.isoformat()
    else:
        result = obj
    return result
