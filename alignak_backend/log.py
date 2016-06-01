#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ``alignak_backend.log`` module
    ======================

    Logging functions
"""

import os
import logging
from logging.handlers import TimedRotatingFileHandler

# Default root logger
root = logging.getLogger()
# Default log format and log level set as WARNING level
logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
                    level=logging.WARNING)


class Log(object):
    """
        Logger for the application
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.namespace = "{modulename}.{classname}".format(
            classname=self.__class__.__name__,
            modulename=self.__module__
        )
        self.log = logging.getLogger(self.namespace)

        # Default log level set as WARNING
        self.log.setLevel(logging.WARNING)

    def set_file_logger(self,
                        path='logs', filename='backend.log',
                        when="D", interval=1, backupCount=6):  # pragma: no cover
        # pylint: disable=too-many-arguments
        """
        Configure handler for file logging ...

        :param test: test mode for application
        :type test: boolean
        """
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

        # Store logs in a daily file, keeping 6 days along ...
        fh = TimedRotatingFileHandler(
            filename=os.path.join(path, filename),
            when=when, interval=interval,
            backupCount=backupCount
        )

        # create formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # add the handler to logger
        self.log.addHandler(fh)
