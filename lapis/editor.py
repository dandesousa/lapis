#!/usr/bin/env python
# encoding: utf-8


from subprocess import call


default_editor = "vim"


class EditorInterface(object):
    __editor__ = None

    def open(self, filename):
        call([self.__editor__, filename])


class TrivialEditor(EditorInterface):
    def __init__(self, name):
        self.__editor__ = name


class VIMEditor(EditorInterface):
    __editor__ = "vim"


def interface_for_editor(editor_name):
    if editor_name == "vim":
        return VIMEditor()
    else:
        return TrivialEditor(editor_name)  # TODO: introduce a warning message that gets invoked when command fails to warn users
