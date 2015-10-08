#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess


class TestRun(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['alignak_backend', 'start'])
        time.sleep(5)

    def test_send_to_backend_livehost(self):
        try:
            r = requests.get('http://127.0.0.1:5000/docs')
        except:
            r = 0
        self.assertEqual(r.status_code, 200)

    @classmethod
    def tearDownClass(cls):
        cls.p.kill()
