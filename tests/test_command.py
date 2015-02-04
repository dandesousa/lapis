#!/usr/bin/env python
# encoding: utf-8

import tempfile
import os
import unittest
import io
from lapis.store import Store


class TestStore(unittest.TestCase):
    """tests store related functions"""

    def setUp(self):
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__content_path = ""
        self.__store = Store(self.__sqlite_file.name, self.__content_path)
        self.__pelican_config = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        from pelican.settings import read_settings
        settings = read_settings(self.__pelican_config, override={"SITEURL": os.path.abspath(os.curdir)})
        root_path = os.path.abspath(os.path.dirname(self.__pelican_config))
        self.__store.sync(settings)

        # bogus mock config obj
        self.config = type("Config", (object,), {})()
        self.config.store = self.__store

    def tearDown(self):
        self.__sqlite_file.close()

    def test_list_tags_command(self):
        from lapis.command import ListTagsCommand
        str_io = io.StringIO()
        ListTagsCommand.run(ostream=str_io, config=self.config)
        expected = """bird [1]
cliff [1]
crane [1]
ocean [1]
photography [2]
shore [1]
water [2]
"""
        self.assertEqual(expected, str_io.getvalue())
