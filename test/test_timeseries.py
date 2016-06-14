#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check preparation of timeseries
"""

import time
import unittest2
from alignak_backend.timeseries import Timeseries


class TestRTimeseries(unittest2.TestCase):
    """
    This class test timepseries preparation
    """

    def test_prepare_data(self):
        """
        Prepare timeseries from a web perfdata

        :return: None
        """
        item = {
            'host': 'srv001',
            'service': 'check_xxx',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'NGINX OK -  0.161 sec. response time, Active: 25 (Writing: 3 Reading: 0 '
                      'Waiting: 22) ReqPerSec: 58.000 ConnPerSec: 1.200 ReqPerConn: 4.466',
            'long_output': '',
            'perf_data': 'Writing=3;;;; Reading=0;;;; Waiting=22;;;; Active=25;1000;2000;; '
                         'ReqPerSec=58.000000;100;200;; ConnPerSec=1.200000;200;300;; '
                         'ReqPerConn=4.465602;;;;',
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'ReqPerConn',
                    'value': {
                        'name': 'ReqPerConn',
                        'min': None,
                        'max': None,
                        'value': 4.465602,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'Writing',
                    'value': {
                        'name': 'Writing',
                        'min': None,
                        'max': None,
                        'value': 3,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'Waiting',
                    'value': {
                        'name': 'Waiting',
                        'min': None,
                        'max': None,
                        'value': 22,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'ConnPerSec',
                    'value': {
                        'name': 'ConnPerSec',
                        'min': None,
                        'max': None,
                        'value': 1.2,
                        'warning': 200,
                        'critical': 300,
                        'uom': ''
                    }
                },
                {
                    'name': 'Active',
                    'value': {
                        'name': 'Active',
                        'min': None,
                        'max': None,
                        'value': 25,
                        'warning': 1000,
                        'critical': 2000,
                        'uom': ''
                    }
                },
                {
                    'name': 'ReqPerSec',
                    'value': {
                        'name': 'ReqPerSec',
                        'min': None,
                        'max': None,
                        'value': 58,
                        'warning': 100,
                        'critical': 200,
                        'uom': ''
                    }
                },
                {
                    'name': 'Reading',
                    'value': {
                        'name': 'Reading',
                        'min': None,
                        'max': None,
                        'value': 0,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                }
            ]
        }
        self.assertEqual(reference, ret)
