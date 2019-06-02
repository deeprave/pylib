#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    xml_indent
    add (or remove) whitespace to an xml.ElementTree for pretty printing
    requires an ElementTree or similar interface (works with elementtree,
    and probably lxml)
"""
from typing import Any

__all__ = (
    'xml_indent'
)


def _text_indent(text, indent):
    # type: (str, str) -> str
    """
    indent a block of text
    :param str text: text to indent
    :param str indent: string to indent with
    :return: the rendered result (with no trailing indent)
    """
    lines = [line.strip() for line in text.strip().split('\n')]
    return indent + indent.join(lines)


def xml_indent(elem, level=0, indent=2):
    # type: (Any, int, int) -> Any
    """

    :param ElementTree elem: Parsed tree of XML elements
    :param int level: recursion level
    :param int indent: number of spaces to indent
    :return: the element tree, adjusted for XML formatting
    """

    if indent <= 0:
        elem.tail = None
        elem.text = elem.text.strip() if elem.text else None
        if len(elem):
            for e in elem:
                xml_indent(e, level + 1, indent)
    else:
        u = (' ' * indent) if indent else ''
        i = '\n' + (u * level)
        j = '\n' + (u * (level - 1))
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + u
            elif '\n' in elem.text:
                elem.text = _text_indent(elem.text, i)
            for e in elem:
                xml_indent(e, level + 1, indent)
                if not e.tail or not e.tail.strip():
                    e.tail = i + u
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if not elem.tail or not elem.tail.strip():
                if level:
                    elem.tail = i + u
                else:
                    elem.tail = '\n'
            if elem.text and elem.text.strip() and '\n' in elem.text:
                elem.text = _text_indent(elem.text, i + u) + i
    return elem

