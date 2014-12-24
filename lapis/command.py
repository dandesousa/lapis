#!/usr/bin/env python
# encoding: utf-8

"""Entry point for the command line interface to Lapis"""


from argparse import ArgumentParser
import logging


PROG = "lapis"



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


def main(argv=None):
    parser = ArgumentParser(prog=PROG, description="Utility for performing common pelican tasks.")
    parser.add_argument("-v", "--verbose", action="count", help="logging verbosity (more gives additional details)")

    # sub-commands
    subparsers = parser.add_subparsers()
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
