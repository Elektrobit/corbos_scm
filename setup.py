#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os import path
from setuptools import setup
from setuptools.command import sdist as setuptools_sdist

import distutils
import subprocess

from corbos_scm.version import __version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

config = {
    'name': 'corbos_scm',
    'long_description': long_description,
    'long_description_content_type': 'text/x-rst',
    'description': 'Corbos SCM - OBS service',
    'author': 'Marcus Schäfer',
    'url': 'https://github.com/schaefi/corbos_scm',
    'author_email': 'marcus.schaefer@gmail.com',
    'version': __version__,
    'license' : 'GPLv3+',
    'install_requires': [
        'docopt'
    ],
    'packages': ['corbos_scm'],
    'entry_points': {
        'console_scripts': [
            'corbos_scm=corbos_scm.corbos_scm:main'
        ]
    },
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
       # classifier: http://pypi.python.org/pypi?%3Aaction=list_classifiers
       'Development Status :: 2 - Pre-Alpha',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: '
       'GNU General Public License v3 or later (GPLv3+)',
       'Operating System :: POSIX :: Linux',
       'Programming Language :: Python :: 3.6',
       'Programming Language :: Python :: 3.8',
       'Topic :: System :: Operating System',
    ]
}

setup(**config)
