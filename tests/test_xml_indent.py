#!/usr/bin/env python
# -*- coding: utf-8 -*-

from elementtree import ElementTree

from pylib.xml_indent import xml_indent

FIXTURE_XML = """
<root>
  <page_heading>
    <title>This is a title</title>
    <hr clear="auto"/>
  </page_heading>
  <articles>
    <article id="1">
      <title>This is the first article</title>
      <body>
        Lorem ipsum dolor sit amet.
         Sint semper salutatus in nam, sit stet dicunt adolescens no.
      </body>
    </article>
    <article id="2">
    <title>And this is the second article</title>
      <body>
        Mentitum sensibus reprimique mea et, per ad enim utamur albucius.
        Cu usu inermis mentitum. Libris delenit platonem te sed, elit sententiae cu sit.
        Delectus prodesset vis ea, mei esse dolorum gloriatur cu.
      </body>
    </article>
  </articles>
</root>
"""



def test_xml_indent_indent_none():
    parsed = ElementTree.fromstring(FIXTURE_XML)
    compacted = xml_indent(parsed, indent=0)
    result = ElementTree.tostring(compacted)
    # only newlines in embedded text shold remain
    print('Indent 0:\n' + result)
    assert result.count('\n') == 3


def test_xml_indent_indent_4():
    parsed = ElementTree.fromstring(FIXTURE_XML)
    fixed = xml_indent(parsed, indent=4)
    result = ElementTree.tostring(fixed)
    # only newlines in embedded text shold remain
    print('Indent 4:\n' + result)
    assert result.count('\n') == 22
