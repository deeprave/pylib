# -*- coding: utf-8 -*-
import pytest
import six
from pylib.bufferio import BufferIO
from pylib import config
from pylib.attrdict import attrdict

YAML = \
    """
    general:
        - feature 1
        - feature 2
        - feature 3
        - subfeature:
            - item 1
            - item 2
    xyzzy:
        hosts:
            - host 1
            - host 2
            - host 3
    """

DICT = {
    'general': [
        'feature 1',
        'feature 2',
        'feature 3',
        {
            'subfeature': [
                'item 1',
                'item 2'
            ]
        }
    ],
    'xyzzy': {
        'hosts': [
            'host 1',
            'host 2',
            'host 3'
        ]
    }
}

BAD_YAML = \
    """
    general:
        - feature 1
        - feature 2
        - feature 3
        subfeature:
            - item 1
            - item 2
    """


@pytest.fixture(scope='module')
def yaml_config_text():
    return YAML


@pytest.fixture(scope='module')
def yaml_config_bad():
    return BAD_YAML


@pytest.fixture(scope='module')
def yaml_config_file():
    return BufferIO(YAML)


def run_common_tests(cfg):
    assert isinstance(cfg, attrdict)
    assert isinstance(cfg.general, tuple)
    assert 4 == len(cfg.general)
    assert isinstance(cfg.xyzzy, dict)
    assert 'feature 3' == cfg.general[2]
    assert isinstance(cfg.general[3], dict)
    assert cfg.general[3]['subfeature'][0] == 'item 1'
    assert cfg == DICT


def test_read_config_text(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    run_common_tests(cfg)


def test_read_config_file(yaml_config_file):
    cfg = config.parse_config(stream=yaml_config_file)
    run_common_tests(cfg)


def test_read_config_properties(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    assert 'host 2' == cfg.value_of('xyzzy.hosts.1')
    assert 'item 1' == cfg.value_of('general.3.subfeature.0')
    subfeature = cfg.value_of('general.3.subfeature')
    assert isinstance(subfeature, (list, tuple))
    assert 'item 1' == subfeature[0]
    assert 'item 2' == subfeature[1]


def test_read_config_errors(yaml_config_bad):
    with pytest.raises(config.YamlParseException):
        config.parse_config(yaml_config_bad)


def test_read_config_non_existent_key(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    assert cfg.value_of('non.existent.key') is None


def test_read_config_non_existent_key_with_default(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    assert cfg.value_of('non.existent.key', default='foo') == 'foo'


def test_read_config_non_existent_key_raises(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    with pytest.raises(KeyError):
        cfg.value_of('non.existent.key', raise_error=True)


def test_read_config_non_existent_cfg_raises(yaml_config_text):
    cfg = config.parse_config(yaml_config_text, raise_errors=True)
    with pytest.raises(KeyError):
        cfg.value_of('non.existent.key')


def test_read_config_return_config(yaml_config_text):
    cfg = config.parse_config(yaml_config_text, raise_errors=True)
    xyzzy = cfg.value_of('xyzzy')
    assert isinstance(xyzzy, attrdict)
    assert hasattr(xyzzy, 'value_of')
    assert xyzzy._raises
    with pytest.raises(KeyError):
        xyzzy.value_of('non.existent.key')


def test_read_config_return_config_in_list(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    general = cfg.value_of('general')
    assert isinstance(general, list)
    assert isinstance(general[3], attrdict)


def test_read_config_return_config_in_list_and_use(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    general = cfg.value_of('general')
    subfeature = general[3].value_of('subfeature')
    assert subfeature == cfg.value_of('general.3.subfeature')


def test_read_config_convert_parse_json(yaml_config_text):
    cfg = config.parse_config(yaml_config_text)
    json_string = cfg.as_json(indent=2)
    assert isinstance(json_string, six.string_types)
    x_cfg = config.parse_config(json_string, as_json=True)
    assert x_cfg == DICT
