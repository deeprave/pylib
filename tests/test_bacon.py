# -*- coding: utf-8 -*-
import os

import pytest

from six import string_types
from pylib.bacon import Parser, combine, Bacon


def test_parser_match_string():
    # NB: Some stings must be passed as raw to preserve escaping
    for test_string in (r"This is a string containg double \"quotes\"", "This is a single 'quote' containing string", 'T', ''):
        parser = Parser('"{}"'.format(test_string))
        string = parser.match_string()
        assert test_string == string.replace('"', '\\"')
        assert parser.index == len(test_string) + 2
        with pytest.raises(ValueError):
            parser.nextch()
    for test_string in ('This is a string containg double "quotes"', r'This is a single \'quote\' containing string', 'T', ''):
        parser = Parser("'{}'".format(test_string))
        string = parser.match_string()
        assert test_string == string.replace("'", "\\'")
        assert parser.index == len(test_string) + 2
        with pytest.raises(ValueError):
            parser.nextch()


def test_parser_match_integer():
    for test_value in ('12345', '5', '-7'):
        parser = Parser('{}'.format(test_value))
        integer = parser.match_integer()
        assert integer == test_value
        assert parser.index == len(test_value)
        with pytest.raises(ValueError):
            parser.nextch()


def test_parser_match_number():
    for test_value in ('123.0', '1234', '-77', '-22.6', '-22.456e4'):
        parser = Parser('{}'.format(test_value))

        integer, frac, exp = parser.match_number()
        result_value = combine(integer, frac, exp)

        assert result_value == test_value
        assert float(result_value) == float(test_value)
        assert parser.index == len(test_value)
        with pytest.raises(ValueError):
             parser.nextch()


def test_parser_match_whitespace():
    for test_value in ('no leading space', ' 1 leading space',
                       '    \tleading space and tabs'):
        parser = Parser('{}'.format(test_value))
        space = parser.match_whitespace()
        assert test_value.startswith(space)
        rest = parser.seq(length=None)
        assert test_value[len(space):] == rest


def test_parser_match_to_newline():
    for test_value in ('# comment here\n', '; comment block at end, no newline',
                       '    # another comment with leading whitespace\n'):
        parser = Parser('{}'.format(test_value))
        value = parser.match_to_character()
        assert test_value.startswith(value)
        assert parser.index == len(test_value)
        with pytest.raises(ValueError):
             parser.nextch()

FIXTURE = """
# This is an example configuration for syntax testing only

*SECTION1
{
    {
    <
        {  "DEVICE",  "AAALDP"  }
        {  "DEVICE_TYPE",  "AAALDP"  }
        {  "DEVICE_EMULATOR_VERSION",  ""  }
        {  "DEVICE_STATE",
        <>
        }
        {  "COMMAND_COUNTS",
        <>
        }
    >
    }
    {
    <
        {  "DEVICE",  "APOLLO"  }
        {  "DEVICE_TYPE",  "APOLLO"  }
        {  "DEVICE_EMULATOR_VERSION",  ""  }
        {  "DEVICE_STATE",
        <
            {  "ACCOUNTS",
            <>
            }
            {  "CUSTOMERS",
            <>
            }
            {  "CUSTOMER SUBSCRIPTIONS",
            <>
            }
            {  "FRIENDS 'N' FAMILY LISTS",
            <>
            }
            {  "SPEND LIMITS",
            <>
            }
        >
        }
        {  "COMMAND_COUNTS",
        <>
        }
    >
    }
}
"""

def test_section_parser():
    parser = Parser(FIXTURE)
    parsed = parser.parse()
    assert isinstance(parsed, dict)
    assert 'SECTION1' in parsed
    section1 = parsed['SECTION1']
    assert isinstance(section1, list)
    assert len(section1) == 2

def test_bacon_parser():
    bacon = Bacon(FIXTURE)
    parsed = bacon.parse()
    assert isinstance(parsed, dict)
    assert 'SECTION1' in parsed
    parsed = bacon.normalise({'SECTION1': 'DEVICE'})
    section1 = parsed['SECTION1']
    assert isinstance(section1, dict)
    for k, v in section1.items():
        assert v['DEVICE'] == k


def test_bacon_json():
    bacon = Bacon(FIXTURE)
    bacon.normalise({'SECTION1': 'DEVICE'})
    # basically test that this can be rendered without error
    jstring = bacon.json(indent=2, sort_keys=True)
    assert isinstance(jstring, string_types)

