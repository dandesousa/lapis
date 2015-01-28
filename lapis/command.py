#!/usr/bin/env python
# encoding: utf-8

"""Entry point for the command line interface to Lapis"""


from argparse import ArgumentParser
import logging
import os
import sys


logger = logging.getLogger(__name__)


class Command(object):
    """Base class used for grouping commands and their function"""

    def __init__(self, *args, **kwargs):
        """not intended to be implemented by child classes"""
        raise RuntimeError("may not instantiate an instance of a Command object")

    @classmethod
    def setup(cls, subparser):
        """sets up an instance of the command by calling args setup and setting the run method"""
        # creates the parser for options
        parser = subparser.add_parser(cls.__command__, help=cls.__help__)

        # adds the arguments
        cls.args(parser)

        # sets the default function to invoke
        parser.set_defaults(func=cls.run)

    @staticmethod
    def args(parser):
        """adds the arguments to the parser that should be invoked when the command is created, overrides should be staticmethods"""
        raise NotImplemented

    @staticmethod
    def run(*args, **kwargs):
        """the command that should be run when the subcommand is invoked, overriddes should be staticmethods"""
        raise NotImplemented


class FindCommand(Command):
    __command__ = "find"
    __help__ = "finds articles, posts or other content"

    @staticmethod
    def args(parser):
        parser.add_argument("title", nargs="?", default=None, type=str, help="case-insensitive search by the title")
        # TODO: path this will go away eventually
        parser.add_argument("--path", default=False, action="store_true", help="If given, shows the path instead of the title of the content")
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", "--articles", default=False, action="store_true", help="Restricts the list of returned content to articles.")
        group.add_argument("-p", "--pages", default=False, action="store_true", help="Restricts the list of returned content to pages.")
        parser.add_argument("-t", "--tags", default=[], action="append", help="List of tags which the content must contain.")
        parser.add_argument("-c", "--category", default=None, type=str, help="The category that the content must have")
        parser.add_argument("-w", "--author", default=None, type=str, help="The author that the content must have")

    @staticmethod
    def run(*args, **kwargs):
        """finds the content in the store that matches the criteria.

        :param config Config:  TODO
        """
        config = kwargs["config"]
        articles = kwargs.get("articles", False)
        author = kwargs.get("author", None)
        category = kwargs.get("category", None)
        path = kwargs.get("path", False)
        tags = kwargs.get("tags", [])
        title = kwargs.get("title", "")

        logger.info("finding content that matches the criteria")
        content_type = None
        if articles:
            content_type = "article"
        content_list = config.store.search(author=author, title=title, category=category, tags=tags, content_type=content_type)

        def print_title(content):
            print(content)

        def print_path(content):
            print(content.path)

        print_func = print_title
        if path:
            print_func = print_path

        for content in content_list:
            print_func(content)


class SyncCommand(Command):
    __command__ = "sync"
    __help__ = "syncs the local lapis store with the content directory"

    @staticmethod
    def args(parser):
        pass

    @staticmethod
    def run(*args, **kwargs):
        config = kwargs["config"]
        logger.info("syncing with local content directory")
        updated = config.store.sync(config.settings)
        if updated:
            logger.info("updated metadata for files")
        else:
            logger.info("no change in content -- metadata was not updated")


class ListCommand(Command):
    @staticmethod
    def args(parser):
        parser.add_argument("pattern", nargs="?", default="", type=str, help="regex pattern to match againt the name")
        parser.add_argument("-c", "--order_by_count", default=False, action="store_true", help="Orders by number of instances instead of name")


    @staticmethod
    def list_and_print(*args, **kwargs):
        model = args[0]
        config = kwargs["config"]
        pattern = kwargs.get("pattern", "")
        order_by_count = kwargs.get("order_by_count", False)

        order_by = "content" if order_by_count else "name"
        for obj in config.store.list(pattern, order_by=order_by, cls=model):
            print("{} [{}]".format(obj.name, len(obj.content)))


class ListTagsCommand(ListCommand):
    __command__ = "tags"
    __help__ = "lists existing tags on your pelican site"

    @staticmethod
    def run(*args, **kwargs):
        from lapis.models import Tag
        ListCommand.list_and_print(Tag, *args, **kwargs)


class ListAuthorsCommand(ListCommand):
    __command__ = "authors"
    __help__ = "lists existing authors on your pelican site"

    @staticmethod
    def run(*args, **kwargs):
        from lapis.models import Author
        ListCommand.list_and_print(Author, *args, **kwargs)


sub_command_classes = (FindCommand,
                       SyncCommand,
                       ListTagsCommand,
                       ListAuthorsCommand)


def _parse_args():
    """parses the command arguments"""
    parser = ArgumentParser(prog="lapis", description="Utility for performing common pelican tasks.")
    parser.add_argument("-v", "--verbose", default=0, action="count", help="logging verbosity (more gives additional details)")
    parser.add_argument("-c", "--pelican_config", default=os.path.join(os.curdir, "pelicanconf.py"), help="path to the pelican configuration file used by blog (default: %(default)s)")
    parser.add_argument("--db_name", default=".lapisdb", help="The name of the lapis db file used for caching, stored in the pelican site's root directory (default: %(default)s)")

    # sub-commands
    subparsers = parser.add_subparsers()
    for command_cls in sub_command_classes:
        command_cls.setup(subparsers)

    # TODO: additional sub-commands go here

    args = parser.parse_args()

    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logging.basicConfig(format="%(levelname)s %(asctime)s: %(message)s", level=level)

    # catch-all for unset function
    args._parser = parser
    if not hasattr(args, "func"):
        args.func = invalid_command

    return args


def invalid_command(args):
    args._parser.error("Must select a valid lapis command.")


def main():
    args = _parse_args()

    if not os.path.isfile(args.pelican_config):
        logger.error("Expected pelican configuration file at '{}', setup config or override with -c, --pelican_config".format(args.pelican_config))
        sys.exit(1)

    args.config = type("Config", (object,), {})

    from pelican.settings import read_settings
    args.config.settings = read_settings(args.pelican_config)
    args.config.root_path = os.path.abspath(os.path.dirname(args.pelican_config))
    args.config.content_path = args.config.settings.get('PATH', args.config.root_path)
    args.config.lapis_db_path = os.path.join(args.config.root_path, args.db_name)

    from lapis.store import Store
    args.config.store = Store(args.config.lapis_db_path, args.config.content_path)
    if args.config.store.schema_changed:
        logger.info("migrating to new database format")
        del args.config.store
        os.remove(args.config.lapis_db_path)
        args.config.store = Store(args.config.lapis_db_path, args.config.content_path)

    # if we just created it, sync it, otherwise call the command
    kwargs = {key: value for key, value in args.__dict__.items()}
    if args.config.store.created:
        SyncCommand.run(**kwargs)
        if args.func != SyncCommand.run:
            args.func(**kwargs)
    else:
        args.func(**kwargs)
