#!/usr/bin/env python
# encoding: utf-8

"""module with functions for generating slugs"""


import os
from lapis.formats import default_format


def slugify(title):
    """Simple function that turns a title into a slug

    :param title str: Title of the content
    """
    return title.lower().replace(" ", "-")


def unique_path_and_slug(title, directory, format=default_format, append=0):
    """Simple function that returns a path to a non-existent file suitable for a new file

    :param title str: Title of the content
    :param ext str: Extension to make part of the slug
    :param directory str: Root directory where the slug will be created
    :rtype tuple: tuple of path, slug generated
    """
    slugified = slugify(title)

    while True:
        slug = slugified if not append else "{}-{}".format(slugified, append)
        file_name = "{}.{}".format(slug, format.extension)
        path = os.path.join(directory, file_name)
        if not os.path.exists(path):
            break
        append += 1

    return path, slug
