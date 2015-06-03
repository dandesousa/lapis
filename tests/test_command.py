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
from lapis.config import Config


class TestCommand(unittest.TestCase):
    """tests unit test to test the command module, most of these are meant to exercise the function so we get coverage and no unexpected errors occur
    though they are not particular thorough tests."""

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
        self.config.example_lapis_configuration_file = Config(self.__pelican_config).example_lapis_configuration_file
        self.config.settings = settings
        from lapis.writer import DEFAULT_TEMPLATE_PATH
        self.config.template_path = DEFAULT_TEMPLATE_PATH
        self.config.store = self.__store
        self.str_io = io.StringIO()
        self.config.printer = CommandPrinter(stream=self.str_io)
        self.config.editor = TrivialEditor("echo")
        self.__tmp_dir = tempfile.mkdtemp()
        self.config.content_path = self.__tmp_dir
        self.config.article_path = self.__tmp_dir
        self.config.page_path = self.__tmp_dir
        self.config.preferred_article_dir = lambda date_created, category: os.path.join(self.config.content_path, category, str(date_created.year), str(date_created.month), str(date_created.day))

    def tearDown(self):
        self.__sqlite_file.close()
        shutil.rmtree(self.__tmp_dir)

    def test_command_init(self):
        from lapis.command import Command
        with self.assertRaises(RuntimeError):
            s = Command()

        with self.assertRaises(NotImplementedError):
            Command.args(None)

        with self.assertRaises(NotImplementedError):
            Command.run(None)

    def test_touch_create_uncategorized(self):
        """Tests #46, that we create uncategorized file path when create is run"""
        from lapis.command import CreateCommand
        date_created = datetime.now()
        expected_path = os.path.join(self.config.content_path, "uncategorized", str(date_created.year), str(date_created.month), str(date_created.day))
        CreateCommand.run(config=self.config, content_type="article", title="test", tags=[], category=None, author="", date=date_created, template="default")
        self.assertTrue(os.path.exists(expected_path))

    def test_touch_create_category(self):
        """Tests #46, that we create uncategorized file path when create is run"""
        from lapis.command import CreateCommand
        date_created = datetime.now()
        category = "testcategory"
        expected_path = os.path.join(self.config.content_path, category, str(date_created.year), str(date_created.month), str(date_created.day))
        CreateCommand.run(config=self.config, content_type="article", title="test", tags=[], category=category, author="", date=date_created, template="default")
        self.assertTrue(os.path.exists(expected_path))

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

        with self.assertRaises(SystemExit):
            FindCommand.run(config=self.config, content_type="article", after="2014-01-10", on="2014-01-09")

        with self.assertRaises(SystemExit):
            FindCommand.run(config=self.config, content_type="page", edit=30)

    def test_exercise_main(self):
        from lapis.command import main
        with self.assertRaises(SystemExit):
            args = type("Args", (object,), {})()
            args.pelican_config = "teasdasdla;sd"
            args.config = self.config
            args.content_name = self.__tmp_dir
            args.config.lapis_db_path = self.__sqlite_file.name
            main(args)

        try:
            args = type("Args", (object,), {})()
            args.pelican_config = self.__pelican_config
            args.lapis_config = "~/.asdasdasd.yml"
            args.config = self.config
            args.content_name = self.__tmp_dir
            args.config.lapis_db_path = self.__sqlite_file.name
            main(args)
        except AttributeError:
            pass

    def test_parse_args(self):
        from lapis.command import _parse_args
        try:
            _parse_args()
            self.fail()
        except SystemExit:
            pass

    def test_new_config_command(self):
        from lapis.command import NewConfigCommand
        import filecmp
        tmp_loc = tempfile.NamedTemporaryFile()
        NewConfigCommand.run(config=self.config, location=tmp_loc.name)
        self.assertTrue(filecmp.cmp(tmp_loc.name, self.config.example_lapis_configuration_file))

    def test_exercise_list_authors_command(self):
        from lapis.command import ListAuthorsCommand
        ListAuthorsCommand.run(config=self.config)

    def test_exercise_list_categories_command(self):
        from lapis.command import ListCategoriesCommand
        ListCategoriesCommand.run(config=self.config, reverse=True)

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
