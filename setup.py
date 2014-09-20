#!/usr/bin/env python
# -*- coding: UTF-8 -*-
__author__ = 'd01'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import re
import codecs
import os


# taken from https://github.com/jeffknupp/sandman
here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


readme = open('README.rst').read()


requirements = [
    'requests>=2.4',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='vlcwebclient',
    version=find_version('vlcwebclient.py'),
    description='Control a VLC instance via its webinterface',
    long_description=readme,
    author='Florian Jung',
    author_email='jungflor@gmail.com',
    url='https://github.com/the01/py-vlcwebclient',
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='vlc web interface control',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
