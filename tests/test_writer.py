#!/usr/bin/env python
# encoding: utf-8


import os
import filecmp
import tempfile
import unittest
from datetime import datetime
from lapis.formats import default_format, markdown_description
from lapis.models import Content, Tag, Author, Category
from lapis.writer import write_content


class TestWriter(unittest.TestCase):
    """Test case docstring."""
    __fmt__ = default_format

    def setUp(self):
        self.fmt = self.__fmt__
        self.tempd_path = tempfile.mkdtemp()
        self.data_path = os.path.join(os.path.dirname(__file__), "data")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tempd_path)

    def __find_diffs(self, f1, f2):
        import difflib
        with open(f1, "r", encoding="utf-8") as f:
            s1 = f.readlines()

        with open(f2, "r", encoding="utf-8") as f:
            s2 = f.readlines()

        d = difflib.Differ()
        return list(d.compare(s1, s2))

    def test_write_post(self):
        content = Content(type="page", title="Hello World",
                          author=Author(name="Mr. Greeting"),
                          date_created=datetime.strptime("20150101", "%Y%m%d"))
        expected_file = os.path.join(self.data_path, "expected-page.{}".format(self.fmt.name))
        with tempfile.NamedTemporaryFile("wt", encoding="utf-8") as f:
            write_content(content, f.name, format=self.fmt, content_directory=self.tempd_path)
            f.flush()
            diffs = self.__find_diffs(expected_file, f.name)
            self.assertTrue(filecmp.cmp(expected_file, f.name), "\n".join(diffs))

    def test_write_article(self):
        content = Content(type="article", title="Hello World",
                          date_created=datetime.strptime("20150101", "%Y%m%d"),
                          tags=[Tag(name="hello"), Tag(name="world")],
                          author=Author(name="Mr. Greeting"),
                          category=Category(name="Greetings"))
        expected_file = os.path.join(self.data_path, "expected-article.{}".format(self.fmt.name))
        with tempfile.NamedTemporaryFile("wt", encoding="utf-8") as f:
            write_content(content, f.name, format=self.fmt, content_directory=self.tempd_path)
            f.flush()
            diffs = self.__find_diffs(expected_file, f.name)
            self.assertTrue(filecmp.cmp(expected_file, f.name), "\n".join(diffs))


class TestWriterMarkdown(TestWriter):
    __fmt__ = markdown_description

# TODO: trivial to add other formats, here simply override the __fmt__ property
# and inherit, need to add rst.
