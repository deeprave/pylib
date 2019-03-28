# -*- coding: utf-8 -*-
"""
Define a yaml defined configuration option with the ability to
retrieve values in a flattened dot separated key style
"""
import json
import sys
import six
from .bufferio import BufferIO

import yaml
from pylib.attrdict import attrdict


class ConfigParseException(Exception):

    def __init__(self, *args, **kwargs):
        super(ConfigParseException, self).__init__(*args)
        self._exc = kwargs.get('exc', sys.exc_info())

    def exc_info(self):
        return self._exc


class YamlParseException(ConfigParseException):
    pass


class JsonParseException(ConfigParseException):
    pass


# noinspection PyPep8Naming
class config(attrdict):

    def __init__(self, *args, **kwargs):
        raise_errors = kwargs.pop('raise_errors', None)
        super(config, self).__init__(*args, **kwargs)
        self._setattr('_raises', False if not raise_errors else True)

    def value_of(self, tag, default=None, raise_error=None):
        """ retrieve a configuration item by dot.separated tag """
        # type: (str, object, bool)

        def get_tag_value(_mark, _part):
            if _mark is None:
                return _mark
            if isinstance(_mark, (list, tuple)):     # ensure numeric for list/tuple index
                _part = int(str(_part))
            try:
                return _mark[_part]
            except KeyError:
                raise KeyError("full key: '{}', failed on partial '{}'".format(tag, _part))

        raises = self._raises if raise_error is None else raise_error

        if not tag:
            if raises:
                raise KeyError("blank key is unsupported")
            return default

        mark = self        
        for _tag in tag.split('.'):
            try:
                mark = get_tag_value(mark, _tag)
            except KeyError:
                if raises:
                    raise
                return default
        # if the result returns a dict, make it a config object
        # inherit raises attribute from parent, not from override
        return _make_config_object(mark, self._raises)

    def as_json(self, *args, **kwargs):
        return json.dumps(self, *args, **kwargs)


def _make_config_object(obj, raise_errors):
    # type: (object, bool) -> object
    """ convert a dict to a attrdict and attach a method to retrieve data by dot separated key """
    if isinstance(obj, dict):
        return config(obj, raise_errors=raise_errors)
    if isinstance(obj, (list, tuple, set)):
        return [_make_config_object(member, raise_errors=raise_errors) for member in obj]
    if isinstance(obj, tuple):
        return (_make_config_object(member, raise_errors=raise_errors) for member in obj)
    if isinstance(obj, set):
        return {_make_config_object(member, raise_errors=raise_errors) for member in obj}
    return obj


def _parse_config(stream, raise_errors=None, as_json=False):
    # type: (Union[file, BufferIO], bool, bool) -> attrdict
    try:
        parsed = json.load(stream) if as_json else yaml.safe_load(stream=stream)
    except Exception as exc:
        raise JsonParseException("{}: JSON parse error".format(exc)) \
            if as_json else \
            YamlParseException("{}: YAML parse error".format(exc))
    return config(parsed, raise_errors=raise_errors)


def parse_config(stream=None, raise_errors=False, as_json=False):
    # type: (Union[file, BufferIO, str], bool, bool) -> attrdict
    if stream is None:
        raise ValueError('Requires text or file type for config input')
    if isinstance(stream, six.string_types):
        stream = BufferIO(stream)
    return _parse_config(stream, raise_errors=raise_errors, as_json=as_json)
