# lapis

A utility for managing content on your pelican blog. It indexes and makes your content searchable on the command-line.

**Lapis is not ready for public use**, until it is, see [pelican-shovel](https://github.com/dandesousa/pelican-shovel)

![](https://travis-ci.org/dandesousa/lapis.svg?branch=master) [![Coverage Status](https://coveralls.io/repos/dandesousa/lapis/badge.svg)](https://coveralls.io/r/dandesousa/lapis) [![Documentation Status](https://readthedocs.org/projects/lapis/badge/?version=latest)](https://readthedocs.org/projects/lapis/?badge=latest)

## Documentation

[Complete documentation is available here](http://lapis.readthedocs.org/en/latest/)

### Quick Links

[Installation](http://lapis.readthedocs.org/en/latest/)

## Requirements

* Python 3.3+
* Pelican >= 3.5
* SQLAlchemy
* termcolor [for colored output]
* PyYaml
* Markdown

### You don't support python 2.7.X?! Whaaaaa...

Lapis was written initially to only support python 3. I investigated back-porting to python2.7 and in fact, would not be substantial work. However, I believe lapis is exactly the type of project that allows it to easily support 3 only. Because pelican blogs usually exist inside of virtualenvs containing only a personal website, there is typically not a high barrier to users to upgrade to python 3. Either you aren't touch python, in which case version is largely irrelevant, or you can easily upgrade to python 3 (pelican and most plugins support it).

While python 2.7 support is extended to 2020, it seems silly to continue to support what is, for all intents and purposes, a 5 year old, deprecated version of the language. Instead I will use this as my *tiny tiny tiny* push to get people to start upgrading. Hopefully this is enough to convince you to do so. If not, you are free to fork lapis and create a python 2.7 compatible version.

## Contributions

If you have a feature request, feel free to make a request in the issues section and open up a discussion. If you have already made a change and would like to incorporate it into lapis, submit a pull request and it will be reviewed and discussed. Contributions are greatly appreciated but never required!

## Motivation & Goals

I started this project because I wanted a tool that would make certain tasks easier when managing my personal website. I wanted to be able to easily search pelican content and metadata, easily create and edit content without remembering the exact file path, manage resources outside of the traditional role of pelican (images, documents).

## License
<a rel="license" href="http://creativecommons.org/publicdomain/zero/1.0/"><img src="http://i.creativecommons.org/p/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" /></a>
<br>
Lapis is licensed under CC0, or public domain in all jursidictions that permit it.
