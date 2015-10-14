#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
del os.link

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

import alignak_backend

setup(
    name="Alignak_backend",
    version=alignak_backend.__version__,

    # metadata for upload to PyPI
    author="Alignak team contribution",
    author_email="d.durieux@siprossii.com",
    keywords="alignak monitoring backend",
    url="https://github.com/Alignak-monitoring-contrib/alignak-backend",
    description="Alignak REST Backend",
    long_description=open('README.rst').read(),

    zip_safe=False,

    packages=find_packages(),
    data_files = [('/usr/local/etc/alignak_backend', ['etc/settings.ini'])],
    include_package_data=True,

    install_requires=['Eve', 'flask-bootstrap'],

    entry_points={
        'console_scripts': [
            'alignak_backend = alignak_backend.main:main',
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
