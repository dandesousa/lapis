#!/usr/bin/env python
# encoding: utf-8


import os
import tempfile
import unittest


class TestSlug(unittest.TestCase):
    """tests features related to creating slugs"""

    def setUp(self):
        self.tempd_path = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tempd_path)

    def test_title(self):
        from lapis.slug import slugify
        slug = slugify("The World's Greatest Title")
        self.assertTrue("the-world's-greatest-title", slug)

    def test_unique_path_and_slug_single(self):
        from lapis.slug import unique_path_and_slug
        from lapis.slug import slugify
        from lapis.formats import default_format
        title = "My Unique Title"
        path, slug = unique_path_and_slug(title, self.tempd_path)
        self.assertEqual(os.path.dirname(path), self.tempd_path)
        expected_fn = slugify(title) + "." + default_format.extension
        self.assertEqual(expected_fn, os.path.basename(path))
        self.assertEqual(slug, slugify(title))

    def test_unique_path_and_slug_existing(self):
        from lapis.slug import unique_path_and_slug
        from lapis.slug import slugify
        title = "My Unique Title"
        path, slug = unique_path_and_slug(title, self.tempd_path)
        self.assertEqual(slug, slugify(title))
        prev_slugs = [slug]
        for i in range(100):
            with open(path, "w"):
                pass
            path, slug = unique_path_and_slug(title, self.tempd_path)
            self.assertNotIn(slug, prev_slugs)
            prev_slugs.append(slug)
            self.assertFalse(os.path.exists(path))
