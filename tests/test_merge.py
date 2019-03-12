# -*- coding: utf-8 -*-
from pylib.merge import merge


def test_merge_simple_no_overlap():
    left = dict(a=1, b=2, c=3)
    right = dict(d=4, e=5, f=6, g=7)
    result = merge(left, right)
    assert 7 == len(result)
    for k in left:
        assert left[k] == result[k]
    for k in right:
        assert right[k] == result[k]


def test_merge_overlap():
    left = dict(a=1, b=2, c=3)
    right = dict(_=0, a=4, b=5, d=6, e=7)
    result = merge(left, right)
    assert 6 == len(result)
    for v, k in zip((4, 5, 3, 6, 7, 0), ('a', 'b', 'c', 'd', 'e', '_')):
        assert v == result[k], '{} equals {}'.format(v, result[k])


def test_merge_overlap_complex():
    left = dict(a=1, b=2, c=3, d=dict(e=7, f=8), e=2, f=0)
    right = dict(_=0, a=4, b=5, d=6, e=7, f=dict(a=1, b=2))
    result = merge(left, right)
    assert 7 == len(result)
    assert 6 == result['d']    # simple right overwrites complex left
    assert dict(a=1, b=2) == result['f']   # complex right overwrites simple left


def test_merge_overlap_recursive():
    left = dict(a=1, b=2, c=3, d=dict(e=7, f=8), e=2, f=0)
    right = dict(_=0, a=4, b=5, d=dict(a=1, f=10), e=7, f=dict(a=1, b=2))
    result = merge(left, right)
    assert 7 == len(result)
    assert dict(a=1, e=7, f=10) == result['d']    # complex right merges complex left
