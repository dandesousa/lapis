#!/usr/bin/env python
# encoding: utf-8

"""Entry point for the command line interface to Lapis"""


from argparse import ArgumentParser
import logging
import os
import sys


PROG = "lapis"


def _setup_find_args(sp):
    """add arguments and commands for creating content

    :param sp object: subparsers special action object in argparse used to add sub-commands
    """
    parser = sp.add_parser("find", help="finds articles, posts or other content.")
    parser.add_argument("-p", "--path", default=False, action="store_true", help="If given, shows the path instead of the title of the content")
    parser.set_defaults(func=find)
    sub = parser.add_subparsers()

def _setup_sync_args(sp):
    """add arguments and commands for creating content

    :param sp object: subparsers special action object in argparse used to add sub-commands
    """
    parser = sp.add_parser("sync", help="syncs the local lapis store with the content directory")
    parser.set_defaults(func=sync)
    sub = parser.add_subparsers()

def _setup_create_args(sp):
    """add arguments and commands for creating content

    :param sp object: subparsers special action object in argparse used to add sub-commands
    """
    parser = sp.add_parser("create", help="creates new content")
    sub = parser.add_subparsers()
    _setup_create_post_args(sub)
    _setup_create_page_args(sub)


def _setup_create_post_args(sp):
    help_txt = "creates a new post"
    parser = sp.add_parser("post", help=help_txt, description=help_txt)


def _setup_create_page_args(sp):
    help_txt = "creates a new page"
    parser = sp.add_parser("page", help=help_txt, description=help_txt)


def _parse_args():
    """parses the command arguments"""
    parser = ArgumentParser(prog=PROG, description="Utility for performing common pelican tasks.")
    parser.add_argument("-v", "--verbose", default=0, action="count", help="logging verbosity (more gives additional details)")
    parser.add_argument("-c", "--pelican_config", default=os.path.join(os.curdir, "pelicanconf.py"), help="path to the pelican configuration file used by blog (default: %(default)s)")
    parser.add_argument("--db_name", default=".lapisdb", help="The name of the lapis db file used for caching, stored in the pelican site's root directory (default: %(default)s)")

    # sub-commands
    subparsers = parser.add_subparsers()
    _setup_sync_args(subparsers)
    _setup_find_args(subparsers)
    _setup_create_args(subparsers)

    # TODO: additional sub-commands go here

    args = parser.parse_args()

    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    else:
        level = logging.WARNING

    logging.basicConfig(format="%(levelname)s %(asctime)s: %(message)s")
    logger = logging.getLogger(PROG)
    logger.setLevel(level)
    args.logger = logger

    # catch-all for unset function
    args._parser = parser
    if not hasattr(args, "func"):
        args.func = invalid_command

    return args


def invalid_command(args):
    args._parser.error("Must select a valid lapis command.")


def find(args):
    args.logger.info("finding content that matches the criteria")
    content_list = args.config.store.search()

    def print_title(content):
        print("{} -- {} ({})".format(content.type, content.title, ", ".join(["({}) {}".format(tag.id, tag.name) for tag in content.tags])))

    def print_path(content):
        print(content.path)

    print_func = print_title
    if args.path:
        print_func = print_path

    for content in content_list:
        print_func(content)


def sync(args):
    args.logger.info("syncing with local content directory")
    updated = args.config.store.sync(args.config.settings)
    if updated:
        args.logger.info("updated metadata for files")
    else:
        args.logger.info("no change in content -- metadata was not updated")


def main():
    args = _parse_args()

    if not os.path.isfile(args.pelican_config):
        args.logger.error("Expected pelican configuration file at '{}', setup config or override with -c, --pelican_config".format(args.pelican_config))
        sys.exit(1)

    args.config = type("Config", (object,), {})

    from pelican.settings import read_settings
    args.config.settings = read_settings(args.pelican_config)
    args.config.root_path = os.path.abspath(os.path.dirname(args.pelican_config))
    args.config.content_path = args.config.settings.get('PATH', args.config.root_path)
    args.config.lapis_db_path = os.path.join(args.config.root_path, args.db_name)

    from lapis.store import Store
    args.config.store = Store(args.config.lapis_db_path, args.config.content_path)
    args.func(args)
    #store.sync(settings)
    #from pprint import pprint
    #pprint(settings)