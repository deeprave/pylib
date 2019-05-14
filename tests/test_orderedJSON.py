# -*- coding: utf-8 -*-
import json
from pylib.ojson import OrderedJSONEncoder
from pylib.odict import odict


planets = [
    # name, moons, diameter, distance_from_sun, day_length
    ('Mercury', 0, 4879, 57, 4223),
    ('Venus', 0, 12104, 108, 2802),
    ('Earth', 1, 12756, 150, 24),
    ('Mars', 2, 6792, 228, 709, 10),
    ('Jupiter', 67, 142984, 779, 11),
    ('Saturn', 62, 120536, 1430, 11),
    ('Uranus', 27, 51118, 2880, 17),
    ('Neptune', 14, 49528, 4500, 16),
    ('Pluto', 5, 2370, 5910, 153),
]
fields = ['name', 'moons', 'diameter',  'distance', 'daylength']
planet_names = [p[0] for p in planets]


def make_fixture():
    dct = odict()
    for planet in planets:
        sdct = odict()
        for index, field in enumerate(fields):
            sdct.update((field, planet[index]))
        dct[planet[0]] = sdct
    return dct


def order_is_ok(dct, keys):
    for n, v in zip(dct.keys(), keys):
        assert n == v
    return True


def check_order(dct):
    assert order_is_ok(dct, planet_names)
    for k, p in dct.items():
        assert order_is_ok(p, fields)
    return True


def test_make_fixture(fixture=make_fixture):
    # check sanity of the data first
    f = fixture()
    print('%r' % f)
    assert f is not None
    check_order(f)


def loads(*args, **kwargs):
    kwargs.update(object_pairs_hook=odict)
    return json.loads(*args, **kwargs)


def dumps(*args, **kwargs):
    kwargs.update(cls=OrderedJSONEncoder)
    return json.dumps(*args, **kwargs)


def test_serialize(fixture=make_fixture):
    json_string = dumps(fixture(), )
    json_data = loads(json_string)
    assert check_order(json_data)
