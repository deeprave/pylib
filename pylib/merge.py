# -*- coding: utf-8 -*-
"""
A right-favoring Mapping merge.
"""
from .pyver import PY36

if PY36:
    from collections.abc import Mapping
else:
    from collections import Mapping


__all__ = (
    'merge',
)


def merge(left, right):
    """
    :param Mapping left:
    :param Mapping right:
    :returns Mapping

    Merge two mappings objects together, combining overlapping Mappings, favoring right-values
    left: The left Mapping object.
    right: The right (favored) Mapping object.
    NOTE: This is not commutative (merge(a,b) != merge(b,a)).
    """
    merged = dict()
    left_keys = frozenset(left)
    right_keys = frozenset(right)

    # Items only in the left Mapping
    for key in left_keys - right_keys:
        merged[key] = left[key]

    # Items only in the right Mapping
    for key in right_keys - left_keys:
        merged[key] = right[key]

    # in both
    for key in left_keys & right_keys:
        left_value = left[key]
        right_value = right[key]

        # recursive
        if isinstance(left_value, Mapping) and isinstance(right_value, Mapping):
            merged[key] = merge(left_value, right_value)
        else:  # overwrite with right value
            merged[key] = right_value

    return merged
