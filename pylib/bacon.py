# -*- coding: utf-8 -*-
"""
BACON configuration parser
This is a simplistic implementation that does not support many of the
directives required for a full configuration data loader.
It implements enough to handle Mediator state files only.
"""
from __future__ import unicode_literals

import logging
import sys
import os
import json

import jsonpath_rw_ext as jsonpath
# noinspection PyProtectedMember
from dictdiffer import diff, patch, are_different, EPSILON

from pylib.cleaner import cleaner

byte_types = (bytes, bytearray) if sys.version_info[0] >= 3 else (str,)


__all__ = (
    'Parser',
    'Bacon',
    'MatchType',
    'Delta',
)


INFINITY = float('inf')
NEG_INFINITY = float('-inf')
NAN = float('nan')
FLOAT_CONSTANTS = {
    '-Infinity': INFINITY,
    'Infinity': NEG_INFINITY,
    'NaN': NAN,
}
NUMBER = '0123456789'
HEX_NUMBER = '0123456789abcdefABCDEF'
BACKSLASH = {
    '"': '"',
    '\'': '\'',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}
CONTROL_CHAR = [
    '\b',
    '\f',
    '\n',
    '\r',
    '\t'
]
WHITESPACE_STR = ' \t\n\r'
ESCAPE_Python_2_Text = {
    '\\': '\\\\',
    '"': '\\"',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}
# predefined encoding
DEFAULT_ENCODING = "utf-8"
UNICODE_ENCODING = 'unicode'


def combine(*args):
    """ utility function """
    return ''.join([arg for arg in args if arg is not None])


class Parser(object):

    def __init__(self, string=None, source=None, encoding=None):
        self.encoding = encoding or DEFAULT_ENCODING
        self._filename = None
        self.string = None
        self.length = 0
        self.index = 0
        self.recursion_level = 0
        self.setup(string, source)

    @property
    def filename(self):
        return self._filename

    @property
    def basename(self):
        return '<>' if not self.filename else \
            self.filename if self.filename.startswith('<') else \
            os.path.basename(self.filename)

    def set_filename(self, filename=None, stream=None):
        self._filename = filename if filename else '<{}>'.format(stream)

    def setup(self, string=None, source=None, encoding=None):
        """
        Set a new string to parse, also resets position to strt
        :param str string: string to parse
        :param Any source: file or object with read
        :param str encoding: encoding to use
        :return: None

        Take care of encoding issues right at the start
        """
        if encoding:
            self.encoding = encoding

        def read(_source):
            if hasattr(_source, 'read'):
                self.set_filename(stream='stream')
                return _source.read()
            with open(_source, 'rt') as fp:
                self.set_filename(_source)
                return fp.read()

        def encode(_string):
            if isinstance(_string, byte_types):
                if self.encoding != UNICODE_ENCODING:
                    _string = _string.decode(self.encoding)
                else:
                    _string = _string.decode('utf8')
            return _string

        if string:
            self.set_filename(stream='text')
        else:
            string = read(source)

        self.string = "" if not string else encode(string)
        self.length = len(string)
        self.index = 0

    def output_err(self, msg, start=None, end=None):

        if start is None:
            start = self.index
        if end is None:
            end = start + 1

        def get_line_col(_string, _start):
            line_num = 1 + _string.count('\n', 0, _start)
            if line_num == 1:
                return line_num, _start
            else:
                col_num = _start - _string.rindex('\n', 0, _start)
                return line_num, col_num

        row, col = get_line_col(self.string, start)
        out = '{}: {}({}:{}) offset {}: "{}"'
        return out.format(msg, self.basename, row, col, start, self.string[start:end])

    def inc(self, by=1):
        self.index = self.length if by >= self.length - self.index else self.index + by
        return self.index

    def dec(self, by=1):
        self.index = 0 if by >= self.index else self.index - by
        return self.index

    @property
    def eos(self):
        return self.index >= self.length

    @property
    def atch(self):
        try:
            return self.string[self.index]
        except IndexError:
            raise ValueError(self.output_err('unexpected end of string'))

    def nextch(self):
        ch = self.atch
        self.inc()
        return ch

    def _bounds(self, start=0, length=1):
        from_pos = self.index + start
        if length is None:      # special case - remainder of string
            length = self.length - from_pos
        to_pos = self.index + start + length
        return from_pos, to_pos

    def seq(self, start=0, length=1):
        from_pos, to_pos = self._bounds(start, length)
        return self.string[from_pos:to_pos]

    def nextseq(self, start=0, length=1):
        from_pos, to_pos = self._bounds(start, length)
        chunk = self.string[from_pos:to_pos]
        self.inc(start + length)
        return chunk

    def match_string(self):
        """
        match_string

        match [\", \\, /, \\f, \\b, \\n, \\r, \\t, \\u, chars] begin at s[idx], return matched string
        for a string s = '"abc"', idx should not less than 1, which is the position of 'a',
        or the function will return u'' for nothing found
        """
        # catch index error
        start_index = self.index
        if self.atch not in '"\'':
            raise ValueError(self.output_err("String must start with a quote"))
        quote = self.nextch()
        try:
            char = ""
            while True:
                ch = self.nextch()
                if ch == quote:   # reached the end of the string
                    return char
                elif ch == '\\':
                    # find backslash
                    ch = self.nextch()
                    pos = self.index
                    if ch == 'u':
                        # find \uxxxx
                        nums = self.nextseq(0, 4)
                        # check the four char is num
                        for num in nums:
                            if num not in HEX_NUMBER:
                                raise ValueError(self.output_err("Invalid \\uXXXX", pos, pos + 4))
                        return chr(int(nums, 16))
                    else:
                        # control char
                        try:
                            char += BACKSLASH[ch]
                        except KeyError:
                            raise ValueError(self.output_err('Invalid \\escape: ' + repr(ch), pos))
                elif ch <= '\x1f':
                    raise ValueError(self.output_err('Invalid control character'))
                else:   # find normal characters
                    char += ch
        except IndexError:
            pass
        raise ValueError(self.output_err("Unterminated string", start_index))

    def match_integer(self):
        """
        greedily match integer of [0123456789]
        """
        integer = ''
        while not self.eos:
            if self.atch in NUMBER or (not integer and self.atch in '+-'):
                integer += self.nextch()
            else:
                break
        return integer

    def match_number(self):
        """
        match a valid number of int or float
        """
        integer, frac, exp = None, None, None

        # get integer part
        integer = self.match_integer()

        # get frac part
        if not self.eos and self.atch == '.':
            frac = self.nextch()
            frac += self.match_integer()
        # check fraction which only has '.'
        if frac and frac == '.':
            return None, None

        # get exp part
        if not self.eos and self.atch in 'eE':
            exp_pos = self.index    # may need to rewind
            exp = self.nextch()
            if self.atch in '+-':
                exp += self.nextch()
            _int = self.match_integer()
            if _int:
                exp += _int
            else:
                exp = ''
                self.index = exp_pos

        # check number validity
        if (integer == '-' or integer == '') and (frac == '.' or frac == ''):
            integer, frac, exp = None, None, None

        return integer, frac, exp

    def match_whitespace(self):
        """
        greedily match white spaces, return white spaces matched and index follows
        """
        # type: (str, int)
        white_space = ''
        while not self.eos:
            if self.atch in WHITESPACE_STR:
                white_space += self.nextch()
            else:
                break
        return white_space

    def match_to_character(self, chars='\n'):
        """
        match everything until newline, return the line and index follows
        """
        content = ''
        while not self.eos:
            ch = self.nextch()
            if ch in chars:
                break
            else:
                content += ch
        return content

    def parse_string(self):
        """
        Return a unicode Python representation of a Bacon string
        """
        trunks = []
        while True:
            before = self.index
            try:
                _string = self.match_string()
                _ = self.match_whitespace()
                trunks.append(_string)
            except ValueError:
                self.index = before
                break
            if not _string:
                break
        return ''.join(trunks)

    def parse_null(self):
        if self.seq(length=4).lower() == 'null':
            self.inc(4)
            return None
        raise KeyError("'null' expected")

    def parse_true(self):
        if self.seq(length=4).lower() == 'true':
            self.inc(4)
            return True
        raise KeyError("'true' expected")

    def parse_false(self):
        if self.seq(length=5).lower() == 'false':
            self.inc(5)
            return False
        raise KeyError("'false' expected")

    def parse_number(self):
        start_index = self.index
        integer, frac, exp = self.match_number()
        # find number
        if integer or frac:
            # if float
            if frac or exp:
                res = float(combine(integer, frac, exp))
                if res == float('inf') or res == float('-inf') or res == float('nan'):
                    raise ValueError(self.output_err('Number out of range', start_index))
            # else integer
            else:
                res = int(integer)
            return res
        else:
            raise ValueError(self.output_err('Can not parse string', start_index))

    OBJ_START = '{<'

    def parse_object(self):
        # check string or empty

        def complement(char):
            return '}' if char == '{' else '>' if char == '<' else '"' if char == '"' else "'" if char == "'" else None

        def fold_list(_out_dict, _out_list):
            # collapse list into dict where possible
            if _out_list:
                if all((isinstance(v, dict) for v in _out_list)):
                    all_keys = set()
                    for v in _out_list:  # ensure that all keys are unique across dicts
                        keys = set(v.keys())
                        if all_keys.intersection(keys):
                            break
                        all_keys.update(keys)
                    else:
                        # no overlap therefore can safely collapse
                        for v in _out_list:
                            _out_dict.update(v)
                elif all((isinstance(v, list) for v in _out_list)):
                    result = []
                    for v in _out_list:
                        result.extend(v)
                    _out_list = result
            return _out_dict, _out_list

        if self.atch not in self.OBJ_START:
            raise ValueError(self.output_err('Expecting start of object {}'.format(self.OBJ_START)))
        start_obj = self.nextch()
        end_obj = complement(start_obj)
        out_dict, out_list = {}, []
        while True:
            _ = self.match_whitespace()
            if self.atch == end_obj:
                self.inc()
                break

            if self.atch in self.OBJ_START:             # list context
                out_list.append(self.decode_one_value())

            else:                                       # dict context
                key = self.decode_one_value()
                _ = self.match_whitespace()
                if self.atch != ',':                    # singleton value
                    out_list.append(key)
                else:
                    self.inc()
                    _ = self.match_whitespace()
                    # get value & add to dict, coerce key to str
                    out_dict[str(key)] = self.decode_one_value()

        out_dict, out_list = fold_list(out_dict, out_list)
        return out_dict if out_dict or not out_list else out_list

    def parse_section(self):
        _ = self.match_whitespace()
        if self.atch != '*':
            raise ValueError(self.output_err('Expecting start of section "*"'))
        self.inc()
        section_name = self.match_to_character('\t\n ')
        return {section_name: self.decode_one_value()}

    # a function map for decode different json type
    decode_func_map = {
        '"': parse_string,
        '{': parse_object,
        '<': parse_object,
        'n': parse_null,
        't': parse_true,
        'f': parse_false,
        'N': parse_null,
        'T': parse_true,
        'F': parse_false,
    }

    def decode_one_value(self):
        _ = self.match_whitespace()
        if not self.eos:
            level = self.recursion_level
            self.recursion_level += 1
            try:
                ch = self.atch
                if ch == '#':
                    _ = self.match_to_character()
                elif level == 0:
                    if ch == '*':
                        return self.parse_section()
                    # add other top level directives here...
                    else:
                        raise ValueError(self.output_err('Expected start of section marker "*"'))
                else:
                    try:
                        return self.decode_func_map[ch](self)
                    except KeyError:
                        return self.parse_number()
            finally:
                self.recursion_level = level

    def _parse(self):
        top_level_dict = {}
        while not self.eos:
            value = self.decode_one_value()
            if value:
                top_level_dict.update(value)
        return top_level_dict

    # noinspection PyShadowingBuiltins
    def parse(self, string=None, file=None):
        if string is None and file:
            string = file.read()
        if string is not None:
            self.setup(string=string)
        return self._parse()

    # noinspection PyShadowingBuiltins
    def parsefile(self, file=None):
        return self.parse(file=file)


# noinspection PyClassHasNoInit
class MatchType:
    ABSENT = 'absent'
    PRESENT = 'present'
    EQUAL = 'equal'
    IEQUAL = "iequal"
    NOTEQUAL = 'notequal'
    CONTAINS = 'contains'
    ICONTAINS = 'icontains'
    CUSTOM = 'custom'


class Bacon(object):

    def __init__(self, string=None, source=None, encoding=None):
        self.parser = Parser(string=string, source=source, encoding=encoding)
        self.parsed = None
        self.normalised = False

    # noinspection PyShadowingBuiltins
    def parse(self, string=None, file=None, normalise=False):
        if not self.parsed:
            self.parsed = self.parser.parse(string=string, file=file)
        if normalise and not self.normalised:
            self.parsed = self.normalise_devices()
            self.normalised = True
        return self.parsed

    def patch(self, delta):
        self.parse()
        return self.parsed if not delta else patch(delta, self.parsed, in_place=True)

    def json(self, **kwargs):
        parsed = self.parse()
        return json.dumps(parsed, **kwargs)

    def find(self, path):
        jpath = jsonpath.parse(path)
        for found in jpath.find(self.parse()):
            try:
                return str(found.value)
            except (AttributeError, KeyError):
                pass
        return None

    MATCH = {
        MatchType.ABSENT:
            lambda found, match, matchfunc: False if found else True,
        MatchType.PRESENT:
            lambda found, match, matchfunc: True if found else False,
        MatchType.EQUAL:
            lambda found, match, matchfunc: found == match,
        MatchType.IEQUAL:
            lambda found, match, matchfunc: (found.lower() if found else "") == (match.lower() if match else ""),
        MatchType.NOTEQUAL:
            lambda found, match, matchfunc: found != match,
        MatchType.CONTAINS:
            lambda found, match, matchfunc: match in found,
        MatchType.ICONTAINS:
            lambda found, match, matchfunc: (match.lower() if match else "") in (found.lower() if found else ""),
        MatchType.CUSTOM:
            lambda found, match, matchfunc: matchfunc(found, match),
    }

    def matches(self, path, match=None, matchtype=None, matchfunc=None):
        found = self.find(path)
        if matchfunc:
            return matchfunc(found, match), found
        if matchtype is None:
            matchtype = MatchType.EQUAL
        return self.MATCH[matchtype](found, match, matchfunc), found

    def normalise(self, pairs):
        """convert a list of items into a dict using a common attribute"""
        parsed = self.parse()

        for key, subkey in pairs.items():

            def merge_list(to_merge):
                result = {}
                for item in to_merge:
                    result[item[subkey]] = item
                return result

            def flatten(element):
                if isinstance(element, dict):
                    if key in element:
                        try:
                            element[key] = merge_list(element[key])
                        except KeyError:
                            pass
                    else:
                        for k, v in element.items():
                            flatten(v)
                elif isinstance(element, list):
                    for v in element:
                        flatten(v)

            flatten(parsed)

        self.parsed = parsed
        return parsed

    DEVICE_SPEC = {'DEVICES': 'DEVICE'}

    def normalise_devices(self):
        """typical for state files"""
        return self.normalise(self.DEVICE_SPEC)

    def __repr__(self):
        return '<Bacon {} len={}> at 0x{:x}'.format(self.parser.basename, self.parser.length, id(self))


def clean_counts(value):
    return value is not None and value != 'COMMAND_COUNTS'


class Delta(object):

    def __init__(self, original, changed, cleanfunc=None):
        self.files = [None, None]
        self.bacon = [None, None]
        self.parsed = [False, False]
        for index, nfile in enumerate((original, changed)):
            if isinstance(nfile, Bacon):
                self.files[index] = 'file {}'.format(index+1)
            else:
                self.files[index] = nfile
                nfile = Bacon(source=nfile)
            self.bacon[index] = nfile
        self._diff = None
        self._diff_kwargs = dict()
        self._cleaner = cleanfunc or clean_counts

    def _parse(self, index):
        if not self.parsed[index]:
            logging.debug('Parsing %s', self.files[index])
            self.parsed[index] = True
        return self.bacon[index].parse(normalise=True)

    def are_different(self):
        tolerance = self._diff_kwargs.get('tolerance', EPSILON)
        return are_different(self._parse(0), self._parse(1), tolerance)

    def diff(self, clean=True, **kwargs):
        """
        difference two BACON files
        :param bool clean: whether to clean
        :param kwargs: as follows
        : node=None ignore=None path_limit=None
        : expand=False tolerance=EPSILON dot_notation=True
        :see: dictdiff.diff for details
        :return:
        """
        if self._diff is None or self._diff_kwargs != kwargs:
            parse = [self._parse(0), self._parse(1)]
            if clean:
                parse[0] = cleaner(parse[0], self._cleaner, key_only=True)
                parse[1] = cleaner(parse[1], self._cleaner, key_only=True)
            self._diff = diff(parse[0], parse[1], **kwargs)
            self._diff_kwargs = dict(kwargs)
        if self._diff:
            return [item for item in self._diff]
        return None

