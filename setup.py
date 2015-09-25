#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import os
del os.link

import alignak_backend

setup(
    name="alignak_backend",
    version=alignak_backend.__version__,

    # metadata for upload to PyPI
    author="Alignak team",
    author_email="d.durieux@siprossii.com",
    keywords="alignak monitoring",
    url="https://github.com/Alignak-monitoring-contrib/alignak-backend",
    description="Alignak REST Backend",
    long_description=open('README.rst').read(),

    packages = ['alignak_backend'],

    install_requires=['Eve', 'flask-bootstrap'],

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
