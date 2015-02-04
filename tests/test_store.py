#!/usr/bin/env python
# encoding: utf-8

import tempfile
import os
import unittest
from lapis.store import Store


class TestStore(unittest.TestCase):
    """tests store related functions"""

    def setUp(self):
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__store = Store(self.__sqlite_file.name)

        from lapis.models import Tag
        self.__store.get_or_create(Tag, name="tag1")
        self.__store.get_or_create(Tag, name="tag2")
        self.__store.get_or_create(Tag, name="tag3")

    def tearDown(self):
        self.__sqlite_file.close()

    def test_store_delete(self):
        """tests that the session closes with no errors"""
        del self.__store

    def test_tag_list(self):
        """tests that all tags exist and that they are returned when the regular expression is right"""
        from lapis.models import Tag
        tag_list = ("tag1", "tag2", "tag3")

        tags = list(self.__store.list("", cls=Tag))
        self.assertEqual(3, len(tags))
        self.assertTrue(all((tag.name in tag_list for tag in tags)))

        tags = list(self.__store.list("^tag", cls=Tag))
        self.assertEqual(3, len(tags))
        self.assertTrue(all((tag.name in tag_list for tag in tags)))

        tags = list(self.__store.list("^tag2", cls=Tag))
        self.assertEqual(1, len(tags))
        self.assertTrue(tags[0].name == "tag2")

    def test_empty_tags(self):
        from lapis.models import Tag
        tags = list(self.__store.list("^fake_tag$", cls=Tag))
        self.assertFalse(tags)


class TestStoreFromDisk(unittest.TestCase):
    """tests that the store is properly synced from disk"""

    def setUp(self):
        from pelican.settings import read_settings
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__store = Store(self.__sqlite_file.name)
        self.__pelican_config = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        settings = read_settings(self.__pelican_config, override={"SITEURL": os.path.abspath(os.curdir)})
        root_path = os.path.abspath(os.path.dirname(self.__pelican_config))
        content_path = settings.get('PATH', root_path)
        self.__store.sync(settings)

    def tearDown(self):
        pass

    def test_search_cardinality(self):
        self.assertEqual(1, len(list(self.__store.search(content_type="page"))))
        self.assertEqual(2, len(list(self.__store.search(content_type="article"))))

    def test_search_date_range(self):
        from datetime import datetime
        fmt = "%Y%m%d"
        dates = (datetime.strptime("20140304", fmt),)
        self.assertEqual(0, len(list(self.__store.search(dates=dates))))
        dates = (datetime.strptime("20140309", fmt),)
        self.assertEqual(1, len(list(self.__store.search(dates=dates))))
        dates = (datetime.strptime("20140309", fmt), datetime.strptime("20141212", fmt), )
        self.assertEqual(2, len(list(self.__store.search(dates=dates, content_type="article"))))
        self.assertEqual(1, len(list(self.__store.search(dates=dates, content_type="page"))))
