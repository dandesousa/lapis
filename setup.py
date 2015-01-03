"""\
Lapis
"""
import os
import sys
from setuptools import setup, find_packages


if sys.argv[-1] == 'publish':
    sys.exit(os.system('python setup.py sdist upload'))


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

setup(
    name='lapis',
    version='0.1.0',
    description='Perform pelican tasks easily',
    long_description=__doc__,
    author='Daniel DeSousa',
    author_email='dan+lapis@desousa.cc',
    url='http://github.com/dandesousa/lapis',
    license='CC0 1.0 Universal',
    platforms='any',
    packages=find_packages(),
    package_data={'': ['LICENSE'], 'lapis': []},
    install_requires=read('requirements.txt'),
    zip_safe=False,
    entry_points={'console_scripts': ['lapis = lapis.command:main']},
)