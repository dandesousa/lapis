#!/usr/bin/env python
# encoding: utf-8

"""Entry point for the command line interface to Lapis"""

from argparse import ArgumentParser
from datetime import datetime
from lapis.config import Config
from lapis.store import Store
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
        cls._parser = parser

    @staticmethod
    def args(parser):
        """adds the arguments to the parser that should be invoked when the command is created, overrides should be staticmethods"""
        raise NotImplementedError

    @staticmethod
    def run(*args, **kwargs):
        """the command that should be run when the subcommand is invoked, overriddes should be staticmethods"""
        raise NotImplementedError


class NewConfigCommand(Command):
    __command__ = "newconfig"
    __help__ = "generates a new configuration file for the user"

    @staticmethod
    def args(parser):
        parser.add_argument("-l", "--location", default=os.path.join(os.path.expanduser("~"), ".lapis.yml"), type=str, help="the location to generate the lapis configuration file (default: %(default)s)")

    @staticmethod
    def run(*args, **kwargs):
        import shutil
        config = kwargs["config"]
        dst = kwargs.get("location", None)
        shutil.copyfile(config.example_lapis_configuration_file, dst, follow_symlinks=True)
        print("Your new lapis configuration file can be found at: {}".format(dst))


class FindCommand(Command):
    __command__ = "find"
    __help__ = "finds articles, posts or other content"

    @staticmethod
    def args(parser):
        parser.add_argument("content_type", choices=("page", "article", ), type=str, help="the content type that should be searched for")
        parser.add_argument("title", nargs="?", default=None, type=str, help="case-insensitive search by the title")
        parser.add_argument("-s", "--status", default=None, choices=("published", "hidden", "draft"), help="The status that the content must have.")
        parser.add_argument("-t", "--tags", default=[], action="append", help="List of tags which the content must contain.")
        parser.add_argument("-c", "--category", default=None, type=str, help="The category that the content must have")
        parser.add_argument("-w", "--author", default=None, type=str, help="The author that the content must have")
        parser.add_argument("-b", "--before", default=None, type=str, help="created before the the given date (format: YYYY-MM-DD)")
        parser.add_argument("-a", "--after", default=None, type=str, help="created after the the given date (format: YYYY-MM-DD)")
        parser.add_argument("-d", "--on", default=None, type=str, help="created on the the given date (format: YYYY-MM-DD)")
        parser.add_argument("-e", "--edit", default=None, type=int, help="Edits the Nth (1-len(content)) found content.")
        parser.add_argument("-p", "--path", default=None, type=int, help="Prints the source path of the Nth (1-len(content)) found content.")
        parser.add_argument("--delete", default=None, type=int, help="Deletes the content located at the given source path.")

    @staticmethod
    def run(*args, **kwargs):
        config = kwargs["config"]
        author = kwargs.get("author", None)
        category = kwargs.get("category", None)
        tags = kwargs.get("tags", [])
        title = kwargs.get("title", "")
        status = kwargs.get("status", None)
        edit_num = kwargs.get("edit", None)
        path_num = kwargs.get("path", None)
        delete_num = kwargs.get("delete", None)

        try:
            fmt = "%Y-%m-%d"

            def parsed_date(s):
                if s in kwargs and kwargs[s]:
                    return datetime.strptime(kwargs[s], fmt)
                return None
            after_date = parsed_date("after")
            before_date = parsed_date("before")
            on_date = parsed_date("on")
        except ValueError:
            logger.error("invalid date format, must specify {}".format(fmt))
            sys.exit(1)
        else:
            if on_date and (after_date or before_date):
                logger.error("must specify either --on or (--before, --after) but not both.")
                sys.exit(1)
            elif after_date and before_date and after_date > before_date:
                logger.error("value specified for --after should come prior to value in --before")
                sys.exit(1)

        dates = (after_date, before_date) if not on_date else (on_date,)
        logger.info("finding content that matches the criteria")
        content_type = kwargs["content_type"]
        content_list = list(config.store.search(author=author, status=status, title=title, category=category, tags=tags, content_type=content_type, dates=dates))

        def edit_action(content):
            config.editor.open(content.source_path)
            config.store.sync_file(config.settings, content.source_path, content.type)

        def path_action(content):
            config.printer.print_location(content)

        def delete_action(content):
            while True:
                config.printer.print_delete_confirmation(content)
                choice = sys.stdin.readline().strip()
                if choice == "y":
                    os.remove(content.source_path)
                    config.store.purge()
                    config.printer.print_delete_acknowledgement(content)
                    break
                elif choice == "n":
                    break

        priority_action = None
        content_num = None
        if edit_num is not None:
            priority_action = edit_action
            content_num = edit_num
        elif path_num is not None:
            priority_action = path_action
            content_num = path_num
        elif delete_num is not None:
            priority_action = delete_action
            content_num = delete_num

        if priority_action:
            valid_range = list(range(len(content_list)))
            if content_num-1 in valid_range:
                content = content_list[content_num-1]
                if os.path.exists(content.source_path):
                    priority_action(content)
                else:
                    sys.stderr.write("It appears as though you manually removed the file at {}.\nRun 'lapis sync' to purge it and search again.\n".format(content.source_path))
                    sys.exit(1)
            else:
                if len(valid_range) == 1:
                    range_str = "1"
                else:
                    range_str = "1-{}".format(valid_range[-1] + 1)
                config.printer.print_content(content_list)
                sys.stderr.write("{} is not in the range of available items found. Re-run with {}\n".format(content_num, range_str))
                sys.exit(1)
        else:
            config.printer.print_content(content_list)


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


class CreateCommand(Command):
    __command__ = "create"
    __help__ = "creates a piece of content."

    @staticmethod
    def args(parser):
        parser.add_argument("content_type", choices=("page", "article", ), default=None, help="the type of content to create")
        parser.add_argument("title", type=str, default=None, help="the title of the post or page to create")
        parser.add_argument("-t", "--tags", default=[], action="append", help="List of tags which the content must contain.")
        parser.add_argument("-c", "--category", default=None, type=str, help="The category that the content must have")
        parser.add_argument("-a", "--author", default=None, type=str, help="The author that the content must have")

    @staticmethod
    def run(*args, **kwargs):
        config = kwargs["config"]
        content_type = kwargs["content_type"]
        title = kwargs["title"]
        tags = kwargs["tags"]
        category = kwargs["category"]
        author = kwargs["author"]
        if author is None:
            author = config.author_name

        from lapis.writer import write_content
        from lapis.slug import unique_path_and_slug
        dest_dir = config.preferred_article_dir() if content_type == "article" else config.page_path
        try:
            os.makedirs(dest_dir)
        except FileExistsError:
            pass
        # TODO: pass in format
        dest_path, slug = unique_path_and_slug(title, dest_dir, date=datetime.now())

        write_content(dest_path, slug, content_type, title=title, tags=tags, category=category, author=author)
        config.editor.open(dest_path)
        config.store.sync_file(config.settings, dest_path, content_type)


class ListCommand(Command):
    @staticmethod
    def args(parser):
        parser.add_argument("pattern", nargs="?", default="", type=str, help="regex pattern to match againt the name")
        parser.add_argument("-c", "--order_by_count", default=False, action="store_true", help="Orders by number of instances instead of name")
        parser.add_argument("-r", "--reverse", default=False, action="store_true", help="Reverses the standard order in which items are displayed")
        parser.add_argument("-z", "--show_zero", default=False, action="store_true", help="Shows items which have a count of zero")

    @staticmethod
    def list_and_print(*args, **kwargs):
        model = args[0]
        config = kwargs["config"]
        pattern = kwargs.get("pattern", "")
        order_by_count = kwargs.get("order_by_count", False)
        reverse = kwargs.get("reverse", False)
        show_zero = kwargs.get("show_zero", False)
        order_by = "content" if order_by_count else "name"
        items = list(config.store.list(pattern, order_by=order_by, cls=model))

        # filters out zero elements
        if not show_zero:
            items = [item for item in items if len(item.content)]

        if reverse:
            items.reverse()

        config.printer.print_content_attributes(items)


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


class ListCategoriesCommand(ListCommand):
    __command__ = "categories"
    __help__ = "lists existing categoriess on your pelican site"

    @staticmethod
    def run(*args, **kwargs):
        from lapis.models import Category
        ListCommand.list_and_print(Category, *args, **kwargs)


sub_command_classes = (FindCommand,
                       CreateCommand,
                       ListAuthorsCommand,
                       ListCategoriesCommand,
                       ListTagsCommand,
                       SyncCommand,
                       NewConfigCommand,
                       )


def _parse_args():
    """parses the command arguments"""
    parser = ArgumentParser(prog="lapis", description="Utility for performing common pelican tasks.")
    parser.add_argument("-v", "--verbose", default=0, action="count", help="logging verbosity (more gives additional details)")
    parser.add_argument("--lapis_config", default=os.path.join(os.path.expanduser("~"), ".lapis.yml"), help="path to the users lapis config file (default: %(default)s)")
    parser.add_argument("--pelican_config", default=os.path.join(os.curdir, "pelicanconf.py"), help="path to the pelican configuration file used by blog (default: %(default)s)")

    # sub-commands
    subparsers = parser.add_subparsers()
    for command_cls in sub_command_classes:
        command_cls.setup(subparsers)

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


def main(args=None):
    if args is None:
        args = _parse_args()

    if not os.path.isfile(args.pelican_config):
        logger.error("Expected pelican configuration file at '{}', setup config or override with -c, --pelican_config".format(args.pelican_config))
        sys.exit(1)

    if not hasattr(args, "config"):
        args.config = Config(args.pelican_config, conf=args.lapis_config)
    try:
        args.config.store = Store(args.config.lapis_db_path)
    except:
        args.config.store = None

    if not args.config.store or args.config.store.schema_changed:
        logger.info("migrating to new database format")
        del args.config.store
        os.remove(args.config.lapis_db_path)
        args.config.store = Store(args.config.lapis_db_path)

    # if we just created it, sync it, otherwise call the command
    kwargs = {key: value for key, value in args.__dict__.items()}
    if args.config.store.created:
        SyncCommand.run(**kwargs)
        if args.func != SyncCommand.run:
            args.func(**kwargs)
    else:
        args.func(**kwargs)

    if args.config.store is not None:
        del args.config.store
