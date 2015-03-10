#!/usr/bin/env python
# encoding: utf-8


"""module containing format information"""

import collections

# how formats are specified
FormatDescription = collections.namedtuple("FormatDescription", ["name", "extension"])

# formats
markdown_description = FormatDescription("markdown", "md")
rst_description = FormatDescription("restructuredtext", "rst")

# extension mappings
supported_formats = {
    'markdown': markdown_description,
    'mkd': markdown_description,
    'md': markdown_description,
    'rst': rst_description,
    'rest': rst_description,
    'restx': rst_description,
    'restructuredtext': rst_description,
}

default_format = supported_formats['markdown']
