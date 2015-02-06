#!/usr/bin/env python
# encoding: utf-8


import sys
import termcolor as tc


class ColorFormatter(object):
    def __init__(self, color_enabled):
        self.__color_enabled = color_enabled

    def get_color_text(self, value, color, attrs=[]):
        if self.__color_enabled:
            return tc.colored(value, color, attrs=attrs)
        else:
            return value

class ContentFormatter(ColorFormatter):
    """Returns string presentations of various attributes for content"""
    def __init__(self, content, **kwargs):
        super().__init__(kwargs.get("color_enabled", False))
        self.__content = content
        self.content_type_id_color = kwargs.get("content_type_id_color", "yellow")
        self.title_color = kwargs.get("title_color", "blue")
        self.status_published_color = kwargs.get("status_published_color", "cyan")
        self.status_other_color = kwargs.get("status_published_color", "red")
        self.author_color = kwargs.get("author_color", "yellow")
        self.date_created_color = kwargs.get("date_color", "yellow")

    @property
    def content_type_id(self):
        return self.get_color_text(self.__content.type.capitalize(), self.content_type_id_color)

    @property
    def status(self):
        return self.get_color_text(self.__content.status.capitalize(), self.status_published_color if self.__content.status == "published" else self.status_other_color)

    @property
    def title(self):
        return self.get_color_text(self.__content.title, self.title_color)

    @property
    def author(self):
        return self.get_color_text(self.__content.author.name, self.author_color)

    @property
    def date_created(self):
        return self.get_color_text(self.__content.date_created.strftime("%Y-%m-%d"), self.date_created_color)

    def __str__(self):
        return "[{}] [{}] [{}] {}".format(self.content_type_id, self.status, self.date_created, self.title)


class ContentAttributeFormatter(ColorFormatter):
    def __init__(self, content_attribute, **kwargs):
        super().__init__(kwargs.get("color_enabled", False))
        self.__content_attribute = content_attribute
        self.count_color = kwargs.get("count_color", "yellow")
        self.name_color = kwargs.get("name_color", "cyan")

    @property
    def count(self):
        return self.get_color_text(len(self.__content_attribute.content), self.count_color)

    @property
    def name(self):
        return self.get_color_text(self.__content_attribute.name, self.name_color)

    def __str__(self):
        return "[{count}] {name}".format(name=self.name, count=self.count)


class CommandPrinter(object):
    """Class responsible for outputting command"""
    def __init__(self, stream=sys.stdout, **kwargs):
        self.__stream = stream
        self.__color_enabled = kwargs.get("color_enabled", False)

    @property
    def color_enabled(self):
        return self.__color_enabled

    def print_content(self, content_list, **kwargs):
        """prints content on the provided stream"""
        for content in content_list:
            print(ContentFormatter(content, color_enabled=self.__color_enabled), file=self.__stream)

    def print_content_attributes(self, content_attributes, **kwargs):
        """prints content attributes like tags, author, etc"""
        for content_attr in content_attributes:
            print(ContentAttributeFormatter(content_attr, color_enabled=self.__color_enabled), file=self.__stream)
