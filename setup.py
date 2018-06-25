#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import os
import sys

from importlib import import_module

try:
    from setuptools import setup, find_packages
except:
    sys.exit("Error: missing python-setuptools library")

long_description = "Python Alignak backend"
try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    pass

# Define the list of requirements with specified versions
def read_requirements(filename='requirements.txt'):
    """Reads the list of requirements from given file.

    :param filename: Filename to read the requirements from.
                     Uses ``'requirements.txt'`` by default.

    :return: Requirments as list of strings.
    """
    # allow for some leeway with the argument
    if not filename.startswith('requirements'):
        filename = 'requirements-' + filename
    if not os.path.splitext(filename)[1]:
        filename += '.txt'  # no extension, add default

    def valid_line(line):
        line = line.strip()
        return line and not any(line.startswith(p) for p in ('#', '-'))

    def extract_requirement(line):
        egg_eq = '#egg='
        if egg_eq in line:
            _, requirement = line.split(egg_eq, 1)
            return requirement
        return line

    with open(filename) as f:
        lines = f.readlines()
        return list(map(extract_requirement, filter(valid_line, lines)))
requirements = read_requirements()

try:
    python_version = sys.version_info
except:
    python_version = (1, 5)
if python_version < (2, 7):
    sys.exit("This application requires a minimum Python 2.7.x, sorry!")

from alignak_backend import __application__, __version__, __copyright__
from alignak_backend import __releasenotes__, __license__, __doc_url__, __git_url__
from alignak_backend import __author__, __author_email__, __classifiers__
from alignak_backend import __name__ as __pkg_name__

package = import_module('alignak_backend')

data_files = [('etc/alignak-backend',
               ['etc/settings.json', 'etc/alignak-backend-logger.json', 'etc/uwsgi.ini',
                'etc/grafana_queries.json', 'etc/grafana_tables.json', 'etc/alignak-backend.wsgi']),
              ('bin',
               ['bin/alignak-backend-uwsgi']),
              ('var/log/alignak-backend', [])]
if 'bsd' in sys.platform or 'dragonfly' in sys.platform:
    data_files.append(('etc/rc.d', ['bin/rc.d/alignak-backend']))

setup(
    name=__pkg_name__,
    version=__version__,

    license=__license__,

    # metadata for upload to PyPI
    author=__author__,
    author_email=__author_email__,
    keywords="alignak monitoring backend",
    url=__git_url__,
    description=package.__doc__.strip(),
    long_description=long_description,
    long_description_content_type='',

    classifiers = __classifiers__,

    zip_safe=False,

    packages=find_packages(),

    # Where to install distributed files
    data_files = data_files,

    # Dependencies (if some) ...
    # Set Flask dependency because of a forced dependency in Eve...
    install_requires=requirements,

    # Entry points (if some) ...
    entry_points={
        'console_scripts': [
            'alignak-backend = alignak_backend.main:main'
        ],
    }
)
