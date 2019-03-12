# -*- coding: utf-8 -*-
from pylib.attrdict import attrdict


def test_attrdict():
    d = attrdict()
    assert isinstance(d, dict)
    r = repr(d)
    assert 'attrdict({})' == r
    s = str(d)
    assert '{}' == s


def test_attrdict_setget():
    d = attrdict()
    d.test = 'test'
    assert 'test' == d.test
    assert 'test' == d['test']


def test_attrdict_nested():
    d = attrdict()
    e = attrdict(test2='test2')
    e.test3 = 'test3'
    d.test = attrdict(e)
    assert 'test2' == d.test.test2
    assert 'test2' == d.test['test2']
    assert 'test3' == d.test.test3
    assert 'test3' == d.test['test3']
