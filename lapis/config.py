#!/usr/bin/env python
# encoding: utf-8


import logging
import os
import yaml

logger = logging.getLogger(__name__)


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

    @property
    def settings(self):
        """the pelican settings dictionary read from the pelicanconf.py"""
        return self.__settings

    @property
    def content_path(self):
        return self.settings['PATH']

    @property
    def article_path(self):
        return os.path.join(self.content_path, self.settings['ARTICLE_PATHS'][0])

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
