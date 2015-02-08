#!/usr/bin/env python
# encoding: utf-8


import logging
import os
import yaml

logger = logging.getLogger(__name__)

from datetime import datetime
from lapis.printer import CommandPrinter


class Config(object):
    """config which encapsulates the attributes of a lapis session configuration"""

    def __init__(self, pelican_config_path, **kwargs):
        from pelican.settings import read_settings
        siteurl_override = os.path.dirname(pelican_config_path)
        self.__settings = read_settings(pelican_config_path, override={"SITEURL": siteurl_override})

        # parse the configuration
        conf_filename = kwargs.get("conf", os.path.join(os.path.expanduser("~"), ".lapis.yml"))
        self.__parse_conf_data(conf_filename)

        # setup printer
        self.__printer = CommandPrinter(color_enabled=self.__tc_enabled)

        # examples
        self.__example_lapis_configuration_file = os.path.join(os.path.dirname(__file__), "examples", "lapis.yml")

    def __parse_conf_data(self, conf_fn):
        """parses the configuration data in the conf file and populates this configs attributes"""
        try:
            with open(conf_fn, "rt", encoding="utf-8") as f:
                data = yaml.load(f)
        except IOError:
            data = {}

        from lapis.editor import interface_for_editor, default_editor
        self.__editor = interface_for_editor(data.get("editor", default_editor))

        from lapis.formats import default_format, supported_formats
        fmt_name = data.get("format", default_format.name)
        self.__format = supported_formats[fmt_name]

        tcdata = data.get("termcolors", {})
        self.__tc_enabled = tcdata.get("enabled", "no") in ("yes", True, 1)

        # paths
        self.__preferred_article_path_format_str = data.get("article_path", "")

    @property
    def settings(self):
        """the pelican settings dictionary read from the pelicanconf.py"""
        return self.__settings

    @property
    def content_path(self):
        return self.settings['PATH']

    @property
    def example_lapis_configuration_file(self):
        return self.__example_lapis_configuration_file

    @property
    def article_path(self):
        return os.path.join(self.content_path, self.settings['ARTICLE_PATHS'][0])

    def preferred_article_dir(self, date_created=None):
        """returns the preferred directory for the article.

        :param date_created datetime: the date of the articles creation
        """
        if date_created is None:
            date_created = datetime.now()
        article_path_fragment = self.__preferred_article_path_format_str.format(year=date_created.year, month=date_created.month, day=date_created.day)
        return os.path.join(self.content_path, article_path_fragment)

    @property
    def page_path(self):
        return os.path.join(self.content_path, self.settings['PAGE_PATHS'][0])

    @property
    def author_name(self):
        return self.settings['AUTHOR']

    @property
    def lapis_db_path(self):
        return os.path.join(self.content_path, ".lapisdb")

    @property
    def printer(self):
        return self.__printer

    @property
    def editor(self):
        return self.__editor

    @property
    def format(self):
        return self.__format
