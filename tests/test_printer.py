#!/usr/bin/env python
# encoding: utf-8


import unittest
from lapis.printer import ColorFormatter


class TestColorFormatter(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_color_enabled_off(self):
        formatter = ColorFormatter(False)
        expected = "some text goes here"
        self.assertEqual(expected, formatter.get_color_text(expected, "red"))

    def test_color_enabled_on(self):
        formatter = ColorFormatter(True)
        expected = "some text goes here"
        self.assertNotEqual(expected, formatter.get_color_text(expected, "red"))
