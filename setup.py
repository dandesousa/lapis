"""\
Lapis
"""
import os
import sys
from setuptools import setup, find_packages

if sys.argv[-1] == 'publish':
    sys.exit(os.system('python setup.py sdist upload'))

requires = ['pelican', 'SQLAlchemy', 'Markdown', 'PyYaml', 'termcolor']

setup(
    name='lapis',
    version='0.1.1b',
    description='Perform pelican tasks easily',
    long_description=__doc__,
    author='Daniel DeSousa',
    author_email='dan+lapis@desousa.cc',
    url='http://github.com/dandesousa/lapis',
    license='CC0 1.0 Universal',
    platforms='any',
    test_suite="tests.test_suite.test_all",
    packages=find_packages(exclude=["tests"]),
    package_data={'': ['LICENSE'], 'lapis': ["templates/*", "examples/*"]},
    include_package_data=True,
    install_requires=requires,
    zip_safe=False,
    entry_points={'console_scripts': ['lapis = lapis.command:main']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
