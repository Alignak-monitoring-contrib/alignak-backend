#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class TestHookLivestate(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
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
        self.assertEqual(r['_items'][0]['business_impact'], 5)
        self.assertEqual(r['_items'][0]['type'], 'host')

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
        self.assertEqual(r['_items'][1]['type'], 'service')

    def test_update_host_business_impact(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        data['host_name'] = 'srv002'
        self.backend.post("host", data)

        # Update business_impact
        datap = {'business_impact': 1}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        self.backend.patch("host/" + rh['_id'], datap, headers)

        # check if business_impact of host changed
        params = {'sort': 'host_name'}
        rh = self.backend.get('host', params)

        self.assertEqual(rh['_items'][0]['business_impact'], 1)
        self.assertEqual(rh['_items'][1]['business_impact'], 5)

        # Check if livestate right updated
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][0]['business_impact'], 1)
        self.assertEqual(r['_items'][1]['business_impact'], 5)

    def test_update_service_business_impact(self):
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
        rs = self.backend.post("service", data)

        # Update business_impact
        datap = {'business_impact': 1}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        self.backend.patch("service/" + rs['_id'], datap, headers)

        # check if business_impact of service changed
        rs = self.backend.get('service')
        self.assertEqual(rs['_items'][0]['business_impact'], 1)

        # Check if livestate right updated
        r = self.backend.get('livestate')

        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['business_impact'], 1)

    def test_display_name_host__display_name(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        self.backend.post("host", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001')

        self.backend.delete("host", {})
        self.backend.delete("livestate", {})
        self.backend.delete("livesynthesis", {})

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        data['alias'] = 'Server 001: srv001 alias'
        rh = self.backend.post("host", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host host_name
        datap = {'host_name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__alias(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['alias'] = 'Server 001: srv001 alias'
        rh = self.backend.post("host", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001 alias')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host host_name
        datap = {'host_name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__host_name(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'srv001')

        # * Case we update host host_name
        datap = {'host_name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'srv001-1')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 1)
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_service__display_name(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc['_items'][0]['_id']
        data['display_name'] = 'ping check of server srv001'
        rs = self.backend.post("service", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check of server srv001')

        self.backend.delete("host", {})
        self.backend.delete("service", {})
        self.backend.delete("livestate", {})
        self.backend.delete("livesynthesis", {})

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc['_items'][0]['_id']
        data['display_name'] = 'ping check of server srv001'
        data['alias'] = 'check ping'
        rs = self.backend.post("service", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service alias
        datap = {'alias': 'check ping'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service service_description
        datap = {'service_description': 'check_ping'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service display_name
        datap = {'display_name': 'ping check of server srv001 (2)'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check of server srv001 (2)')

    def test_display_name_service__alias(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc['_items'][0]['_id']
        data['alias'] = 'ping check alias'
        rs = self.backend.post("service", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check alias')

        # * Case we update service alias
        datap = {'alias': 'ping check alias (2)'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service service_description
        datap = {'service_description': 'check-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service display_name
        datap = {'display_name': 'check ping for srv001'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'check ping for srv001')

    def test_display_name_service__service_description(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc['_items'][0]['_id']
        rs = self.backend.post("service", data)

        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping')

        # * Case we update service service_description
        datap = {'service_description': 'ping-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping-1')

        # * Case we update service alias
        datap = {'alias': 'ping alias'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping alias')

        # * Case we update service display_name
        datap = {'display_name': 'check ping srv001'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(r['_items'][1]['display_name_service'], 'check ping srv001')

    def test_update_display_name_host_and_check_service(self):
        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        rh = self.backend.post("host", data)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['command_name'], "ping")

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc['_items'][0]['_id']
        rs = self.backend.post("service", data)

        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get('livestate')
        self.assertEqual(len(r['_items']), 2)
        self.assertEqual(r['_items'][0]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r['_items'][0]['display_name_service'], '')
        self.assertEqual(r['_items'][1]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r['_items'][1]['display_name_service'], 'ping')
