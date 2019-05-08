# -*- coding: utf-8 -*-
from pylib.cleaner import cleaner

fixture_before = {
    "devices": [
        {
            "name": "dev1",
            "type": "type1",
            "attrs": {
                "attr1": 1,
                "attr2": "two",
                "attr3": 'other',
                "ignore": 'comment',
                'value': 'ignore'
            },
            "ignore": "this"
        }
    ]
}

fixture_after = {
    "devices": [
        {
            "name": "dev1",
            "type": "type1",
            "attrs": {
                "attr1": 1,
                "attr2": "two",
                "attr3": 'other',
            },
        }
    ]
}

fixture_after2 = {
    "devices": [
        {
            "name": "dev1",
            "type": "type1",
            "attrs": {
                "attr1": 1,
                "attr2": "two",
                "attr3": 'other',
                'value': 'ignore'
            },
        }
    ]
}



def test_cleaner():

    def not_ignore(x):
        return x is not None and x != 'ignore'

    cleaned = cleaner(fixture_before, not_ignore)
    assert cleaned == fixture_after

    cleaned = cleaner(fixture_before, not_ignore, key_only=True)
    assert cleaned == fixture_after2
