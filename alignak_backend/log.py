#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" This module is used to manage logs """

import logging

ROOT = logging.getLogger()
logging.basicConfig()


class Log(object):
    """ Class to manage logs
    """

    def __init__(self):

        self.namespace = "{modulename}.{classname}".format(
            classname=self.__class__.__name__,
            modulename=self.__module__
        )
        self.log = logging.getLogger(self.namespace)
