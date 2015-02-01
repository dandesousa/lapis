#!/usr/bin/env python
# encoding: utf-8

"""module repsonsible for writing content data to different formats"""


import os
from jinja2 import Environment, FileSystemLoader
from lapis.formats import default_format

TEMPLATES_DIRECTORY=os.path.join(os.path.dirname(__file__), "templates")
CONTENT_DIRECTORY=os.path.join(os.getcwd(), "content")


def write_content(content, dest_path, format=default_format, content_directory=CONTENT_DIRECTORY):
    """writes the content passed to the given path using the template for the target formats.

    depending on the content type, we select the appropriate template for the format and write
    the content to disk at the specified location.

    :param content lapis.Content: model object representing the content to write
    :param dest_path str: location on disk to write the content
    :param format str: format that the file should be written as
    """
    template_file = "{}-{}.jinja".format(content.type, format.name)
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY))
    template = env.get_template(template_file)

    # creates the content dictionary
    content_dict = dict()
    content_dict["title"] = content.title
    content_dict["tags"] = ", ".join((tag.name for tag in content.tags))
    content_dict["category"] = content.category.name if content.category else ""
    content_dict["author"] = content.author.name if content.author else ""
    content_dict["date"] = content.date_created.strftime("%Y-%m-%d %H:%M") if content.date_created else ""
    content_dict["slug"] = ""
    content_dict["summary"] = ""

    # TODO: stores the rest of the content dictionary

    with open(dest_path,"wt", encoding="utf-8") as f:
        f.write(template.render(**content_dict))
