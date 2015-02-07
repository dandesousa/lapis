#!/usr/bin/env python
# encoding: utf-8


import os
import unittest
from lapis.config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        lapis_conf = os.path.join(os.path.dirname(__file__), "data", "configs", ".lapis.yml")
        pelican_conf = os.path.join(os.path.dirname(__file__), "samplesite", "pelicanconf.py")
        self.content_path = os.path.join(os.path.dirname(__file__), "samplesite")
        self.config = Config(pelican_conf, conf=lapis_conf)

    def tearDown(self):
        pass

    def test_author_name(self):
        expected = self.config.settings['AUTHOR']
        self.assertTrue(expected, self.config.author_name)

    def test_content_path(self):
        expected_path = os.path.join(self.content_path, "content")
        self.assertTrue(os.path.samefile(expected_path, self.config.content_path))

    def test_preferred_article_path(self):
        from datetime import datetime
        d = datetime.now()
        expected_path = os.path.join(self.content_path, "content", "posts", str(d.year), str(d.month), str(d.day))
        self.assertTrue(expected_path, self.config.preferred_article_dir())

    def test_article_path(self):
        expected_path = os.path.join(self.content_path, "content")
        self.assertTrue(os.path.samefile(expected_path, self.config.article_path))

    def test_page_path(self):
        expected_path = os.path.join(self.content_path, "content", "pages")
        self.assertTrue(os.path.samefile(expected_path, self.config.page_path))

    def test_format(self):
        from lapis.formats import markdown_description
        expected = markdown_description
        self.assertEqual(expected, self.config.format)

    def test_editor(self):
        from lapis.editor import VIMEditor
        expected = VIMEditor
        self.assertIsInstance(self.config.editor, expected)

    def test_color_enabled(self):
        self.assertTrue(self.config.printer.color_enabled)
