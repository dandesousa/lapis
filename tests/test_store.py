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


class TestStoreFile(unittest.TestCase):
    """tests that the store is properly synced from disk"""

    def setUp(self):
        from pelican.settings import read_settings
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__store = Store(self.__sqlite_file.name)
        self.__pelican_config = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        self.settings = read_settings(self.__pelican_config, override={"SITEURL": os.path.abspath(os.curdir)})

    def test_article(self):
        self.assertEqual(0, len(list(self.__store.search(content_type="article"))))
        article_path = os.path.join(os.path.dirname(__file__), "samplesite", "content", "posts", "2014", "03", "foo.md")
        self.__store.sync_file(self.settings, article_path, "article")
        self.assertEqual(1, len(list(self.__store.search(content_type="article"))))
        article = list(self.__store.search(content_type="article"))[0]
        self.assertEqual("Foo", article.title)
        self.assertEqual("Photography", article.category.name)

    def test_page(self):
        self.assertEqual(0, len(list(self.__store.search(content_type="page"))))
        page_path = os.path.join(os.path.dirname(__file__), "samplesite", "content", "pages", "about.md")
        self.__store.sync_file(self.settings, page_path, "page")
        self.assertEqual(1, len(list(self.__store.search(content_type="page"))))
        page = list(self.__store.search(content_type="page"))[0]
        self.assertEqual("About", page.title)
        self.assertEqual("Daniel DeSousa", page.author.name)


class TestStoreFromDisk(unittest.TestCase):
    """tests that the store is properly synced from disk"""

    def setUp(self):
        from pelican.settings import read_settings
        self.__sqlite_file = tempfile.NamedTemporaryFile()
        self.__store = Store(self.__sqlite_file.name)
        self.__pelican_config = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        settings = read_settings(self.__pelican_config, override={"SITEURL": os.path.abspath(os.curdir)})
        self.__store.sync(settings)

    def tearDown(self):
        pass

    def test_search_status(self):
        self.assertEqual(2, len(list(self.__store.search(content_type="article", status="published"))))
        self.assertEqual(1, len(list(self.__store.search(content_type="page", status="published"))))
        self.assertEqual(3, len(list(self.__store.search(status="published"))))
        self.assertEqual(1, len(list(self.__store.search(status="hidden"))))
        self.assertEqual(1, len(list(self.__store.search(status="draft"))))

    def test_search_cardinality(self):
        self.assertEqual(5, len(list(self.__store.search())))
        self.assertEqual(2, len(list(self.__store.search(content_type="page"))))
        self.assertEqual(3, len(list(self.__store.search(content_type="article"))))

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
