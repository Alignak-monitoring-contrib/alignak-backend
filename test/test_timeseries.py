#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
import time
from alignak_backend_client.client import Backend
from alignak_backend.timeseries import Timeseries

class TestRTimeseries(unittest2.TestCase):

    @unittest2.skip("Need update it")
    def test_prepare_data(self):
        item = {
            'host_name': 'srv001',
            'service_description': 'check_xxx',
            'state' : 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'NGINX OK -  0.161 sec. response time, Active: 25 (Writing: 3 Reading: 0 Waiting: 22) ReqPerSec: 58.000 ConnPerSec: 1.200 ReqPerConn: 4.466',
            'long_output': '',
            'perf_data': 'Writing=3;;;; Reading=0;;;; Waiting=22;;;; Active=25;1000;2000;; ReqPerSec=58.000000;100;200;; ConnPerSec=1.200000;200;300;; ReqPerConn=4.465602;;;;',
            '_realm': 'All.Propieres'
        }

        Timeseries.after_inserted_loghost([item])
        ret = Timeseries.prepare_data(item)
        print(ret)
        self.assertEqual(1, 2)
