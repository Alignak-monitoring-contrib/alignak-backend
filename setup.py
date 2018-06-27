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

# Get default configuration files recursively
data_files = [
    ('share/alignak-backend', ['requirements.txt']),
    ('share/alignak-backend', ['bin/post-install.sh',
                               'bin/alignak-backend-log-rotate',
                               'bin/alignak-backend-uwsgi'])
]
for dir in ['etc', 'bin/rc.d', 'bin/systemd']:
    for subdir, dirs, files in os.walk(dir):
        # Configuration directory
        target = os.path.join('share/alignak-backend', subdir)
        package_files = [os.path.join(subdir, file) for file in files]
        if package_files:
            data_files.append((target, package_files))

setup(
    name=__pkg_name__,
    version=__version__,

    license=__license__,

    # metadata for upload to PyPI
    author=__author__,
    author_email=__author_email__,
    url=__doc_url__,
    download_url=__git_url__,
    description=package.__doc__.strip(),
    long_description=long_description,
    long_description_content_type='text/x-rst',

    classifiers = __classifiers__,

    keywords='python monitoring alignak nagios shinken',

    project_urls={
        'Presentation': 'http://alignak.net',
        'Documentation': 'http://docs.alignak.net/en/latest/',
        'Source': 'https://github.com/alignak-monitoring-contrib/alignak-backed/',
        'Tracker': 'https://github.com/alignak-monitoring-contrib/alignak-backend/issues',
        'Contributions': 'https://github.com/alignak-monitoring-contrib/'
    },

    # Package data
    packages=find_packages(exclude=['docs', 'test']),
    include_package_data=True,

    # Where to install distributed files
    data_files = data_files,

    # Unzip Egg
    zip_safe=False,
    platforms='any',

    # Dependencies...
    install_requires=requirements,
    dependency_links=[
        # Use the standard PyPi repository
        "https://pypi.python.org/simple/",
    ],

    # Entry points (if some) ...
    entry_points={
        'console_scripts': [
            'alignak-backend = alignak_backend.main:main'
        ],
    }
)
