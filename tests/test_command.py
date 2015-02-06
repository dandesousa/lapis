#!/usr/bin/env python
# encoding: utf-8

import tempfile
import os
import unittest
import io
import shutil
from argparse import ArgumentParser, ArgumentError
from datetime import datetime
from lapis.store import Store
from lapis.printer import CommandPrinter
from lapis.editor import TrivialEditor


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
        self.config.editor = TrivialEditor("echo")
        self.__tmp_dir = tempfile.mkdtemp()
        self.config.content_path = self.__tmp_dir
        self.config.article_path = self.__tmp_dir
        self.config.page_path = self.__tmp_dir

    def tearDown(self):
        self.__sqlite_file.close()
        shutil.rmtree(self.__tmp_dir)

    def test_exercise_create(self):
        from lapis.command import CreateCommand
        CreateCommand.run(config=self.config, content_type="page", title="test", author="", tags=[], category="", date=datetime.now())

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
