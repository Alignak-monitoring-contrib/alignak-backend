#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class TestHookLivetest(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['alignak_backend', 'start'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')
        cls.backend.login("admin", "admin", "force")
        cls.backend.delete("host", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})

    def test_add_host(self):
        data = json.loads(open('cfg/host_srv001.json').read())
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get('host')
        self.assertEqual(rh['_items'][0]['host_name'], "srv001")
        # Check if livestate right created
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['last_state'], 'UNREACHABLE')
        self.assertEqual(r['_items'][0]['last_state_type'], 'HARD')
        self.assertEqual(r['_items'][0]['last_check'], 0)
        self.assertEqual(r['_items'][0]['state_type'], 'HARD')
        self.assertEqual(r['_items'][0]['state'], 'UNREACHABLE')
        self.assertEqual(r['_items'][0]['host_name'], rh['_items'][0]['_id'])
        self.assertEqual(r['_items'][0]['service_description'], None)

    @classmethod
    def tearDownClass(cls):
        cls.backend.delete("host", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})
        cls.backend.delete("contact", {})
        cls.p.kill()
