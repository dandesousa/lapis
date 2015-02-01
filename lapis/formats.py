#!/usr/bin/env python
# encoding: utf-8


"""module containing format information"""

import collections

# how formats are specified
FormatDescription = collections.namedtuple("FormatDescription", ["name", "extension"])

# formats
markdown_description = FormatDescription("markdown", "md")

# extension mappings
supported_formats = {
    'markdown': markdown_description,
    'mkd': markdown_description,
    'md': markdown_description
}

default_format = supported_formats['markdown']
