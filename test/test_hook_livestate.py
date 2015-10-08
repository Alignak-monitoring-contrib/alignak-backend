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

    @classmethod
    def tearDownClass(cls):
        cls.backend.delete("contact", {})
        cls.p.kill()

    @classmethod
    def tearDown(cls):
        cls.backend.delete("host", {})
        cls.backend.delete("service", {})
        cls.backend.delete("command", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})


    def test_add_host(self):
        data = json.loads(open('cfg/host_srv001.json').read())
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get('host')
        self.assertEqual(rh['_items'][0]['host_name'], "srv001")
        self.host_id = rh['_items'][0]['_id']
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

    def test_add_service(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        self.backend.post("host", data)
        rh = self.backend.get('host')

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_items'][0]['_id']
        data['check_command'] = rc['_items'][0]['_id']
        self.backend.post("service", data)
        # Check if service right in backend
        rs = self.backend.get('service')
        self.assertEqual(rs['_items'][0]['service_description'], "ping")

        # Check if livestate right created
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['last_state'], 'OK')
        self.assertEqual(r['_items'][1]['last_state_type'], 'HARD')
        self.assertEqual(r['_items'][1]['last_check'], 0)
        self.assertEqual(r['_items'][1]['state_type'], 'HARD')
        self.assertEqual(r['_items'][1]['state'], 'OK')
        self.assertEqual(r['_items'][1]['host_name'], rh['_items'][0]['_id'])
        self.assertEqual(r['_items'][1]['service_description'], rs['_items'][0]['_id'])
