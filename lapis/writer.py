#!/usr/bin/env python
# encoding: utf-8

"""module repsonsible for writing content data to different formats"""


import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from lapis.formats import default_format


TEMPLATES_DIRECTORY = os.path.join(os.path.dirname(__file__), "templates")


def write_content(dest_path, slug, content_type, **kwargs):
    """writes the content passed to the given path using the template for the target formats.

    depending on the content type, we select the appropriate template for the format and write
    the content to disk at the specified location.

    :param dest_path str: location on disk to write the content
    :param format str: format that the file should be written as
    """
    format = kwargs.get("format", default_format)
    title = kwargs.get("title", "New {}".format(content_type.capitalize()))
    author = kwargs.get("author", "")
    tags = kwargs.get("tags", [])
    category = kwargs.get("category", "")
    date = kwargs.get("date_created", datetime.now())
    status = kwargs.get("status", "published")

    template_file = "{}-{}.jinja".format(content_type, format.name)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY))
    template = env.get_template(template_file)

    # creates the content dictionary
    content_dict = dict()
    content_dict["title"] = title
    content_dict["tags"] = ", ".join(tags)
    content_dict["category"] = category
    content_dict["author"] = author
    content_dict["date"] = date.strftime("%Y-%m-%d %H:%M")
    content_dict["status"] = status
    content_dict["slug"] = slug
    content_dict["summary"] = ""

    with open(dest_path, "wt", encoding="utf-8") as f:
        f.write(template.render(**content_dict))
