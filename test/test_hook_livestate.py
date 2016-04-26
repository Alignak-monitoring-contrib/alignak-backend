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
        realms = cls.backend.get_all('realm')
        for cont in realms:
            cls.realm_all = cont['_id']

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
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        # Check if livestate right created
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['last_state'], 'UNREACHABLE')
        self.assertEqual(r[0]['last_state_type'], 'HARD')
        self.assertEqual(r[0]['last_check'], 0)
        self.assertEqual(r[0]['state_type'], 'HARD')
        self.assertEqual(r[0]['state'], 'UNREACHABLE')
        self.assertEqual(r[0]['host_name'], rh[0]['_id'])
        self.assertEqual(r[0]['service_description'], None)
        self.assertEqual(r[0]['business_impact'], 5)
        self.assertEqual(r[0]['type'], 'host')

    def test_add_service(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        self.backend.post("host", data)
        rh = self.backend.get_all('host')

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh[0]['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        self.backend.post("service", data)
        # Check if service right in backend
        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping")

        # Check if livestate right created
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['last_state'], 'OK')
        self.assertEqual(r[1]['last_state_type'], 'HARD')
        self.assertEqual(r[1]['last_check'], 0)
        self.assertEqual(r[1]['state_type'], 'HARD')
        self.assertEqual(r[1]['state'], 'OK')
        self.assertEqual(r[1]['host_name'], rh[0]['_id'])
        self.assertEqual(r[1]['service_description'], rs[0]['_id'])
        self.assertEqual(r[1]['type'], 'service')

    def test_update_host_business_impact(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        data['name'] = 'srv002'
        self.backend.post("host", data)

        # Update business_impact
        datap = {'business_impact': 1}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        self.backend.patch("host/" + rh['_id'], datap, headers)

        # check if business_impact of host changed
        params = {'sort': 'name'}
        rh = self.backend.get_all('host', params)

        self.assertEqual(rh[0]['business_impact'], 1)
        self.assertEqual(rh[1]['business_impact'], 5)

        # Check if livestate right updated
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]['business_impact'], 1)
        self.assertEqual(r[1]['business_impact'], 5)

    def test_update_service_business_impact(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        self.backend.post("host", data)
        rh = self.backend.get_all('host')

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh[0]['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        # Update business_impact
        datap = {'business_impact': 1}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        self.backend.patch("service/" + rs['_id'], datap, headers)

        # check if business_impact of service changed
        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['business_impact'], 1)

        # Check if livestate right updated
        r = self.backend.get_all('livestate')

        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['business_impact'], 1)

    def test_display_name_host__display_name(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        self.backend.post("host", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        self.backend.delete("host", {})
        self.backend.delete("livestate", {})
        self.backend.delete("livesynthesis", {})

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        data['alias'] = 'Server 001: srv001 alias'
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host host_name
        datap = {'name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__alias(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['alias'] = 'Server 001: srv001 alias'
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001 alias')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host host_name
        datap = {'name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__host_name(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001')

        # * Case we update host host_name
        datap = {'name': 'srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001-1')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_service__display_name(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['display_name'] = 'ping check of server srv001'
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check of server srv001')

        self.backend.delete("host", {})
        self.backend.delete("service", {})
        self.backend.delete("command", {})
        self.backend.delete("livestate", {})
        self.backend.delete("livesynthesis", {})

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['display_name'] = 'ping check of server srv001'
        data['alias'] = 'check ping'
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service alias
        datap = {'alias': 'check ping'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service service_description
        datap = {'name': 'check_ping'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service display_name
        datap = {'display_name': 'ping check of server srv001 (2)'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check of server srv001 (2)')

    def test_display_name_service__alias(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['alias'] = 'ping check alias'
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias')

        # * Case we update service alias
        datap = {'alias': 'ping check alias (2)'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service service_description
        datap = {'name': 'check-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service display_name
        datap = {'display_name': 'check ping for srv001'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'check ping for srv001')

    def test_display_name_service__service_description(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping')

        # * Case we update service service_description
        datap = {'name': 'ping-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping-1')

        # * Case we update service alias
        datap = {'alias': 'ping alias'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping alias')

        # * Case we update service display_name
        datap = {'display_name': 'check ping srv001'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        rs = self.backend.patch("service/" + rs['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'check ping srv001')

    def test_update_display_name_host_and_check_service(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        rh = self.backend.post("host", data)

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        rs = self.backend.post("service", data)

        datap = {'display_name': 'Server 001: srv001-1'}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        rh = self.backend.patch("host/" + rh['_id'], datap, headers)
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[1]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r[1]['display_name_service'], 'ping')

    def test_host_template(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get_all('command')
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        data['_is_template'] = True
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[0]['_is_template'], True)
        # Check if livestate right created
        r = self.backend.get_all('livestate')
        self.assertEqual(len(r), 0)
