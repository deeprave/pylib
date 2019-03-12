# -*- coding: utf-8 -*-
from unittest import TestCase

from pylib.iterable import is_iterable, iterable


class Counter(object):
    """
    Sample iterable class
    """
    def __init__(self, low=1, high=10):
        self.current = self.low = low
        self.high = high

    def __next__(self):
        if self.current > self.high:
            raise StopIteration
        self.current += 1
        return self.current - 1

    def next(self):
        return self.__next__()

    def __iter__(self):
        return self


def generator(start_value, multiplier):
    value = start_value
    while True:
        yield value
        value *= multiplier


# noinspection SpellCheckingInspection
class TestIsIterable(TestCase):

    def test_list_isiterable(self):
        self.assertTrue(is_iterable([]))
        self.assertTrue(is_iterable([1, 3, 4]))
        my_list = [1, 'two', 'FIVE', 9]
        self.assertTrue(is_iterable(my_list))

    def test_iter_isiterable(self):
        self.assertTrue(is_iterable([]))
        my_list_iterator = iter([1, 'two', 'FIVE', 9])
        self.assertTrue(is_iterable(my_list_iterator))

    def test_dict_isiterable(self):
        self.assertTrue(is_iterable({}))
        self.assertTrue(is_iterable({'one': 1, 2: 'two', 'three': 'third'}))
        my_dict = {1: 'one', 'two': 2, 'third': 'three'}
        self.assertTrue(is_iterable(my_dict))

    def test_bytes_isNOTiterable(self):
        self.assertFalse(is_iterable(b''))
        self.assertFalse(is_iterable(b'1234567890abcdefg'))

    def test_str_isNOTiterable(self):
        self.assertFalse(is_iterable(b''))
        self.assertFalse(is_iterable(b'1234567890abcdefg'))

    def test_raw_string_isNOTiterable(self):
        self.assertFalse(is_iterable(r''))
        self.assertFalse(is_iterable(r'\rthis is a raw string\n'))

    def test_iterable_is_iterable(self):
        counter = Counter()
        self.assertTrue(is_iterable(counter))

    def test_generator_is_iterable(self):
        gen_func = generator(1, 2)
        self.assertTrue(is_iterable(gen_func))


class TestIterable(TestCase):

    def test_make_str_iterable(self):
        test_string = 'test string'
        test_strings = iterable(test_string)
        self.assertTrue(is_iterable(test_strings))
        self.assertIn(test_string, test_strings)

    def test_make_bytes_iterable(self):
        test_bytes = b'test string'
        test_bytes_list = iterable(test_bytes)
        self.assertTrue(is_iterable(test_bytes_list))
        self.assertIn(test_bytes, test_bytes_list)

    def test_make_numeric_iterable(self):
        test_numeric = 1234
        test_numeric_list = iterable(test_numeric)
        self.assertTrue(is_iterable(test_numeric_list))
        self.assertIn(test_numeric, test_numeric_list)

    def test_make_floats_iterable(self):
        test_numeric = 1234.056789
        test_numeric_list = iterable(test_numeric)
        self.assertTrue(is_iterable(test_numeric_list))
        self.assertIn(test_numeric, test_numeric_list)

    def test_list_is_already_iterable(self):
        test_list = ['one', 2, 'three', 'four', 5]
        self.assertTrue(is_iterable(test_list))
        test_list2 = iterable(test_list)
        self.assertTrue(is_iterable(test_list2))
        self.assertListEqual(test_list, test_list2)
        self.assertEqual(test_list, test_list2)

    def test_dict_is_already_iterable(self):
        test_dict = {'one': 1, 2: 'two', 'three': 3, 'four': 4, 5: 'five'}
        self.assertTrue(is_iterable(test_dict))
        test_dict2 = iterable(test_dict)
        self.assertTrue(is_iterable(test_dict2))
        self.assertDictEqual(test_dict, test_dict2)
        self.assertEqual(test_dict, test_dict2)
