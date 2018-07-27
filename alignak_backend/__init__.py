#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    Alignak REST backend

    This module is an Alignak REST backend
"""
# Application version and manifest
VERSION = (1, 4, 14)

__application__ = u"Alignak_Backend"
__short_version__ = '.'.join((str(each) for each in VERSION[:2]))
__version__ = '.'.join((str(each) for each in VERSION[:4]))
__author__ = u"Alignak team"
__author_email__ = u"david.durieux@alignak.net"
__copyright__ = u"(c) 2015-2018 - %s" % __author__
__license__ = u"GNU Affero General Public License, version 3"
__description__ = u"Alignak REST backend database"
__releasenotes__ = u"""Alignak REST Backend database"""
__git_url__ = "https://github.com/Alignak-monitoring-contrib/alignak-backend"
__doc_url__ = "http://alignak-backend.readthedocs.org"

__classifiers__ = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Operating System :: POSIX :: Linux',
    'Operating System :: POSIX :: BSD :: FreeBSD',
    'Topic :: System',
    'Topic :: System :: Monitoring',
    'Topic :: System :: Networking :: Monitoring',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

# Application manifest
manifest = {
    'name': __application__,
    'version': __version__,
    'author': __author__,
    'description': __description__,
    'copyright': __copyright__,
    'license': __license__,
    'release': __releasenotes__,
    'doc': __doc_url__
}
