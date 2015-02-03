#!/usr/bin/env python
# encoding: utf-8


import os
import unittest


def test_all():
    return unittest.TestLoader().discover(start_dir=os.path.dirname(__file__))


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(test_all())
