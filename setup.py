#!/usr/bin/env python

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Hardcode Haml",
    version = "0.1.0",
    author = "Thammi",
    author_email = "thammi@chaossource.net",
    description = ("Haml for hardcore coders (and C++/C/... projects)"),
    license = "AGPLv3",
    keywords = "haml template html web",
    url = "http://www.chaossource.net/nymp/",
    packages=['hardcode_haml', 'hardcode_haml.lang'],
    package_dir={'': 'src'},
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: C++",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Pre-processors",
        "Topic :: Text Processing :: Markup :: HTML",
        "Environment :: Console",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
    ],
    entry_points={
        'console_scripts': [
            'hardcode_haml = hardcode_haml.main:main',
            ],
        },
)

