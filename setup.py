#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
del os.link
from importlib import import_module

try:
    from setuptools import setup, find_packages
except:
    sys.exit("Error: missing python-setuptools library")

try:
    python_version = sys.version_info
except:
    python_version = (1, 5)
if python_version < (2, 7):
    sys.exit("This application requires a minimum Python 2.7.x, sorry!")

try:
    from alignak.version import VERSION
    __alignak_version__ = VERSION
except:
    __alignak_version__ = 'x.y.z'

from alignak_backend import __application__, __version__, __copyright__
from alignak_backend import __releasenotes__, __license__, __doc_url__
from alignak_backend import __name__ as __pkg_name__

package = import_module('alignak_backend')

# Define paths
if 'linux' in sys.platform or 'sunos5' in sys.platform:
    paths = {
        'bin':     "/usr/bin",
        'var':     "/var/lib/alignak_backend/",
        'share':   "/var/lib/alignak_backend/share",
        'etc':     "/etc/alignak_backend",
        'run':     "/var/run/alignak_backend",
        'log':     "/var/log/alignak_backend",
        'libexec': "/var/lib/alignak_backend/libexec",
    }
elif 'bsd' in sys.platform or 'dragonfly' in sys.platform:
    paths = {
        'bin':     "/usr/local/bin",
        'var':     "/usr/local/libexec/alignak_backend",
        'share':   "/usr/local/share/alignak_backend",
        'etc':     "/usr/local/etc/alignak_backend",
        'run':     "/var/run/alignak_backend",
        'log':     "/var/log/alignak_backend",
        'libexec': "/usr/local/libexec/alignak_backend/plugins",
    }
else:
    print "Unsupported platform, sorry!"
    exit(1)

setup(
    name=__pkg_name__,
    version=__version__,

    license=__license__,

    # metadata for upload to PyPI
    author="David Durieux",
    author_email="d.durieux@siprossii.com",
    keywords="alignak monitoring backend",
    url="https://github.com/Alignak-monitoring-contrib/alignak-backend",
    description=package.__doc__.strip(),
    long_description=open('README.rst').read(),

    zip_safe=False,

    packages=find_packages(),
    include_package_data=True,
    # package_data={
        # 'sample': ['package_data.dat'],
    # },
    data_files = [(paths['etc'], ['etc/settings.cfg'])],

    install_requires=[
        'Eve', 'flask-bootstrap', 'docopt', 'jsonschema', 'Eve-docs', 'future', 'configparser'
    ],

    entry_points={
        'console_scripts': [
            'alignak_backend = alignak_backend.main:main',
            'cfg_to_backend = alignak_backend.tools.cfg_to_backend:main',
        ],
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration'
    ]
)
