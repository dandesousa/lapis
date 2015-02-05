#!/usr/bin/env python
# encoding: utf-8

import tempfile
import os
import unittest
import io
from lapis.store import Store
from argparse import ArgumentParser, ArgumentError
from lapis.printer import CommandPrinter


class TestStore(unittest.TestCase):
    """tests store related functions"""

    def setUp(self):
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__store = Store(self.__sqlite_file.name)
        self.__pelican_config = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        from pelican.settings import read_settings
        settings = read_settings(self.__pelican_config, override={"SITEURL": os.path.abspath(os.curdir)})
        root_path = os.path.abspath(os.path.dirname(self.__pelican_config))
        self.__store.sync(settings)

        from lapis.command import sub_command_classes
        parser = ArgumentParser(prog="testlapis", description="TestUtility for performing common pelican tasks.")
        # sub-commands
        subparsers = parser.add_subparsers()
        for command_cls in sub_command_classes:
            command_cls.setup(subparsers)

        # bogus mock config obj
        self.config = type("Config", (object,), {})()
        self.config.settings = settings
        self.config.store = self.__store
        self.str_io = io.StringIO()
        self.config.printer = CommandPrinter(stream=self.str_io)

    def tearDown(self):
        self.__sqlite_file.close()

    def test_exercise_sync(self):
        from lapis.command import SyncCommand
        SyncCommand.run(config=self.config)

    def test_exercise_find(self):
        from lapis.command import FindCommand
        FindCommand.run(config=self.config, content_type="page")
        FindCommand.run(config=self.config, content_type="article")

        with self.assertRaises(SystemExit):
            FindCommand.run(config=self.config, content_type="article", after="23123")

        with self.assertRaises(SystemExit):
            FindCommand.run(config=self.config, content_type="article", after="2014-01-10", before="2014-01-09")

    def test_exercise_main(self):
        from lapis.command import main
        with self.assertRaises(SystemExit):
            main()

    def test_list_tags_command(self):
        from lapis.command import ListTagsCommand
        ListTagsCommand.run(config=self.config)
        expected = """[1] bird
[1] cliff
[1] crane
[1] drafts
[1] ocean
[2] photography
[1] shore
[2] water
"""
        self.assertEqual(expected, self.str_io.getvalue())
