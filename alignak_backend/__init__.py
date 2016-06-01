#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Alignak REST backend
"""
# Application manifest
VERSION = (0, 4, 1)

__application__ = u"Alignak_Backend"
__version__ = '.'.join((str(each) for each in VERSION[:4]))
__author__ = u"Alignak team"
__copyright__ = u"(c) 2015 - %s" % __author__
__license__ = u"GNU Affero General Public License, version 3"
__description__ = u"Alignak REST backend"
__releasenotes__ = u"""Alignak REST Backend"""
__doc_url__ = "https://github.com/Alignak-monitoring-contrib/alignak-backend"
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
