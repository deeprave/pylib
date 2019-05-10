# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import OrderedDict
from pylib.idict import idict
from pylib.pyver import *
import pytest


KEYS = ['zero', 'One', 'TwO', 'Three', 'fOUr', 'fivE', 'sIx', 'seven', 'eigHT', 'nInE']
VALUES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
TEST_DICT = OrderedDict()
# need to manually build the dictionary to ensure order is preserved
for k, v in zip(KEYS, VALUES):
    TEST_DICT[k] = v


def test_create():
    d1 = idict(TEST_DICT)
    d2 = idict(**TEST_DICT)
    d3 = idict([(k.upper(), v) for k, v in TEST_DICT.items()])
    d4 = idict([(k.lower(), v) for k, v in TEST_DICT.items()])
    assert d1 == d2
    assert len(d1) == len(KEYS)
    # test for case insensitivity
    assert d1 == d3
    assert d1 == d4

def test_get():
    my_dict = idict(TEST_DICT)
    assert my_dict.get(KEYS[1]) == VALUES[1]
    assert my_dict.get('unknown_key') is None
    assert my_dict.get('unknown_key', None) is None
    with pytest.raises(KeyError):
        _ = my_dict['unknown_key']
    for key in KEYS:
        assert key in my_dict
    my_dict['TEN'] = 10
    assert my_dict['TEN'] == 10


def test_del():
    my_dict = idict(TEST_DICT)
    del my_dict['one']
    assert my_dict.get('one') is None
    with pytest.raises(KeyError):
        _ = my_dict['ONE']
    keys = [_k for _k in KEYS if _k not in ('One', 'one', 'ONE')]
    assert list(my_dict.keys()) == keys


def test_pop():
    my_dict = idict(TEST_DICT)
    one = my_dict.pop('one')
    assert my_dict.get('one') is None
    with pytest.raises(KeyError):
        _ = my_dict['ONE']
    assert 1 == one
    keys = [_k for _k in KEYS if _k is not 'One']
    assert list(my_dict.keys()) == keys


def test_items():
    my_dict = idict(TEST_DICT)
    length = 0
    for key, val in my_dict.items():
        length += 1
        assert key in KEYS
        assert val in VALUES
        assert val == my_dict[key]
    assert len(KEYS) == length


if PY2:
    def test_iteritems():
        my_dict = idict(TEST_DICT)
        length = 0
        # noinspection PyCompatibility
        for key, val in my_dict.iteritems():
            length += 1
            assert key in KEYS
            assert val in VALUES
            assert val == my_dict[key]
        assert len(KEYS) == length


def test_keys():
    my_dict = idict(TEST_DICT)
    length = 0
    for key in my_dict.keys():
        length += 1
        assert key in KEYS
    assert len(KEYS) == length


if PY2:
    def test_iterkeys():
        my_dict = idict(TEST_DICT)
        length = 0
        # noinspection PyCompatibility
        for key in my_dict.iterkeys():
            length += 1
            assert key in KEYS
        assert len(KEYS) == length


def test_values():
    my_dict = idict(TEST_DICT)
    length = 0
    for value in my_dict.values():
        length += 1
        assert value in VALUES
    assert len(VALUES) == length


if PY2:
    def test_itervalues():
        my_dict = idict(TEST_DICT)
        length = 0
        # noinspection PyCompatibility
        for value in my_dict.itervalues():
            length += 1
            assert value in VALUES
        assert len(VALUES) == length


def test_len():
    my_dict = idict(TEST_DICT)
    assert len(KEYS) == len(my_dict)


def test_clear():
    my_dict = idict(TEST_DICT)
    my_dict.clear()
    assert 0 == len(my_dict)
    assert 0 == len(my_dict.keys())


def test_copy():
    o_dict = idict(TEST_DICT)
    my_dict = o_dict.copy()
    assert isinstance(my_dict, idict)
    assert my_dict.get(KEYS[1]) == VALUES[1]
    assert my_dict.get('unknown_key') is None
    with pytest.raises(KeyError):
        _ = my_dict['unknown_key']
    assert list(o_dict.keys()) == KEYS
    assert list(my_dict.keys()) == KEYS


def test_update():
    my_dict = idict()
    my_dict.update(TEST_DICT)
    assert isinstance(my_dict, idict)
    assert my_dict.get('One') == VALUES[1]
    assert my_dict.get('unknown_key') is None
    with pytest.raises(KeyError):
        _ = my_dict['unknown_key']
    my_dict.update(TEN=10)
    assert my_dict['TEN'] == 10
    my_dict.update(eleven=11, twelve=12)
    assert all(key in my_dict for key in ('eleven', 'twelve'))
    my_dict.update({'thirteen': 13, 'fourteen': 14})
    assert all(key in my_dict for key in ('thirteen', 'fourteen'))
    my_dict.update(('fifteen', 15), ('sixteen', 16))
    assert all(key in my_dict for key in ('fifteen', 'sixteen'))
    my_dict.update([('seventeen', 17), ('eighteen', 18)])
    assert all(key in my_dict for key in ('seventeen', 'eighteen'))
    my_dict.update((('nineteen', 19), ('twenty', 20)))
    assert all(key in my_dict for key in ('nineteen', 'twenty'))
    my_dict.update([('twenty_one', 21), ('twenty_two', 22)])
    assert all(key in my_dict for key in ('twenty_one', 'twenty_two'))
    my_dict.update([('twenty_three', 23), ('twenty_four', 24)], twenty_five=25)
    assert all(key in my_dict for key in ('twenty_three', 'twenty_four', 'twenty_five'))


def test_insert():
    my_dict = idict([(_k, _v) for _k, _v in zip(KEYS, VALUES)])
    assert my_dict.get(KEYS[1]) == VALUES[1]
    del my_dict[KEYS[1]]
    assert my_dict.get(KEYS[1]) is None
    with pytest.raises(KeyError):
        _ = my_dict[KEYS[1]]
    assert len(KEYS) - 1 == len(my_dict)

    one = 'oNE'
    my_dict.insert(one, VALUES[1], 1)
    assert my_dict[one] == VALUES[1]
    assert len(KEYS) == len(my_dict)

    keys = list(my_dict.keys())
    keys.insert(0, 'neg1')
    my_dict.insert('neg1', -1, 0)
    assert my_dict['neg1'] == -1
    assert my_dict[one] == VALUES[1]
    assert len(keys) == len(my_dict)
    assert keys == list(my_dict.keys())

    keys.insert(5, 'neg2')
    my_dict.insert('neg2', -2, 5)
    assert my_dict['neg2'] == -2
    assert my_dict[one] == VALUES[1]
    assert len(keys) == len(my_dict)
    assert keys == list(my_dict.keys())

    keys.append('at_end')
    my_dict.insert('at_end', 99)
    assert my_dict['at_end'] == 99
    assert len(KEYS) + 3 == len(my_dict)
    assert len(keys) == len(my_dict)
    assert keys == list(my_dict.keys())


def test_append():
    my_dict = idict([(_k, _v) for _k, _v in zip(KEYS, VALUES)])
    assert my_dict.get(KEYS[1]) == VALUES[1]
    assert len(KEYS) == len(my_dict)

    keys = list(my_dict.keys())
    keys.append('new_key')
    my_dict.append('new_key', 55)
    assert my_dict['new_key'] == 55
    assert len(keys) == len(my_dict)
    assert keys == list(my_dict.keys())


def test_change_value():
    my_dict = idict([(_k, _v) for _k, _v in zip(KEYS, VALUES)])
    assert my_dict.get(KEYS[1]) == VALUES[1]
    assert len(KEYS) == len(my_dict)

    replace = KEYS[5]
    my_dict[replace] = 99
    assert my_dict[replace] == 99


def test_convert():
    my_idict = idict([(_k, _v) for _k, _v in zip(KEYS, VALUES)])
    my_idict.update(nested=my_idict.copy())
    my_normal_dict = {_k: _v for _k, _v in zip(KEYS, VALUES)}
    my_normal_dict.update(nested=my_normal_dict.copy())
    test = idict.convert(my_normal_dict)
    assert my_idict == test
