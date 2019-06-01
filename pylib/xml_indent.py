#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    xml_indent
    add (or remove) whitespace to an xml.ElementTree for pretty printing
"""

__all__ = (
    'xml_indent'
)


def xml_indent(elem, level=0, indent=2):
    i = "\n" + level * "  " if level >= 0 else ''
    j = "\n" + (level - 1) * "  " if level >= 0 else ''
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i
            if level >= 0:
                elem.text += " " * indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            xml_indent(subelem, level + 1 if level >= 0 else level, indent=indent)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem
