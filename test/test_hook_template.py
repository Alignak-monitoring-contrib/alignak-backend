#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import requests
import time
import subprocess
import json
from alignak_backend_client.client import Backend
from alignak_backend.models.host import get_schema as host_schema


class TestHookTemplate(unittest2.TestCase):

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')
        cls.backend.login("admin", "admin", "force")
        cls.backend.delete("host", {})
        cls.backend.delete("command", {})
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

    def test_host_templates(self):
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

        data = {
            'name': 'host_001',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }
        self.backend.post("host", data)

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_command'], rc[0]['_id'])

        schema = host_schema()
        template_fields = []
        ignore_fields = ['name', 'realm', '_template_fields', '_templates', '_is_template']
        for key in schema['schema'].iterkeys():
            if key not in ignore_fields:
                template_fields.append(key)

        self.assertItemsEqual([x.encode('UTF8') for x in rh[1]['_template_fields']], template_fields)

        data = [{
            'name': 'host_002',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }, {
            'name': 'host_003',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }]
        self.backend.post("host", data)

        rh = self.backend.get_all('host')
        self.assertEqual(rh[2]['name'], "host_002")
        self.assertEqual(rh[3]['name'], "host_003")


    def test_host_templates_updates(self):
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

        data = {
            'name': 'host_001',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }
        self.backend.post("host", data)

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_command'], rc[0]['_id'])

        data = {'check_interval': 1}
        resp = self.backend.patch('/'.join(['host', rh[1]['_id']]), data, {'If-Match': rh[1]['_etag']})

        rh = self.backend.get_all('host')
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_interval'], 1)
        if 'check_interval' in rh[1]['_template_fields']:
            self.assertTrue(False, 'check_interval does not be in _template_fields list')

        # update the template
        data = {'initial_state': 'o'}
        self.backend.patch('/'.join(['host', rh[0]['_id']]), data, {'If-Match': rh[0]['_etag']})

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['initial_state'], "o")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['initial_state'], "o")
        if 'initial_state' not in rh[1]['_template_fields']:
            self.assertTrue(False, 'initial_state must be in _template_fields list')

        # update the template name
        data = {'name': 'testhost'}
        self.backend.patch('/'.join(['host', rh[0]['_id']]), data, {'If-Match': rh[0]['_etag']})

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "testhost")
        self.assertEqual(rh[1]['name'], "host_001")


    def test_service_templates(self):
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

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['name'] = 'host_001'
        data['realm'] = self.realm_all
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")

        # add service template
        data = {
            'name': 'ping',
            'host_name': rh[0]['_id'],
            'check_command': rc[0]['_id'],
            'business_impact': 4,
            '_is_template': True,
            '_realm': self.realm_all
        }
        self.backend.post("service", data)
        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping")

        data = {
            'host_name': rh[1]['_id'],
            '_templates': [rs[0]['_id']],
            '_realm': self.realm_all
        }
        self.backend.post("service", data)

        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping")
        self.assertEqual(rs[1]['name'], "ping")
        self.assertEqual(rs[1]['host_name'], rh[1]['_id'])


    def test_service_templates_updates(self):
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

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['name'] = 'host_001'
        data['realm'] = self.realm_all
        self.backend.post("host", data)
        # Check if host right in backend
        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")

        rh = self.backend.get_all('host')
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")

        # add service template
        data = {
            'name': 'ping',
            'host_name': rh[0]['_id'],
            'check_command': rc[0]['_id'],
            'business_impact': 4,
            '_is_template': True,
            '_realm': self.realm_all
        }
        self.backend.post("service", data)
        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping")

        data = {
            'name': 'ping_test',
            'host_name': rh[1]['_id'],
            '_templates': [rs[0]['_id']],
            '_realm': self.realm_all
        }
        self.backend.post("service", data)

        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping")
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['host_name'], rh[1]['_id'])

        data = {'check_interval': 1}
        resp = self.backend.patch('/'.join(['service', rs[1]['_id']]), data, {'If-Match': rs[1]['_etag']})

        rs = self.backend.get_all('service')
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['check_interval'], 1)
        if 'check_interval' in rs[1]['_template_fields']:
            self.assertTrue(False, 'check_interval does not be in _template_fields list')

        # update the template
        data = {'initial_state': 'u'}
        self.backend.patch('/'.join(['service', rs[0]['_id']]), data, {'If-Match': rs[0]['_etag']})

        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['initial_state'], "u")
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['initial_state'], "u")
        if 'initial_state' not in rs[1]['_template_fields']:
            self.assertTrue(False, 'initial_state must be in _template_fields list')

        # update the template name
        data = {'name': 'ping2'}
        self.backend.patch('/'.join(['service', rs[0]['_id']]), data, {'If-Match': rs[0]['_etag']})

        rs = self.backend.get_all('service')
        self.assertEqual(rs[0]['name'], "ping2")
        self.assertEqual(rs[1]['name'], "ping_test")
