#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify the usage of hosts and services templates
"""

import json
import time
import shlex
import subprocess
import requests
import unittest2
from alignak_backend.models.host import get_schema as host_schema


class TestHookTemplate(unittest2.TestCase):
    """
    This class test the hooks used for hosts and services templates
    """

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        """
        This method:
          * delete mongodb database
          * start the backend with uwsgi
          * log in the backend and get the token
          * get the realm

        :return: None
        """
        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % 'alignak-backend')
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000',
                                  '--protocol=http', '--enable-threads', '--pidfile',
                                  '/tmp/uwsgi.pid'])
        time.sleep(3)

        cls.endpoint = 'http://127.0.0.1:5000'

        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin', 'action': 'generate'}
        # get token
        response = requests.post(cls.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth = requests.auth.HTTPBasicAuth(cls.token, '')

        # get realms
        response = requests.get(cls.endpoint + '/realm',
                                auth=cls.auth)
        resp = response.json()
        cls.realm_all = resp['_items'][0]['_id']

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    @classmethod
    def tearDown(cls):
        """
        Delete resources after each test

        :return: None
        """
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_host_templates(self):
        """
        Test host templates

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        data['_is_template'] = True
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")

        data = {
            'name': 'host_001',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_command'], rc[0]['_id'])

        schema = host_schema()
        template_fields = []
        ignore_fields = ['name', 'realm', '_template_fields', '_templates', '_is_template',
                         '_templates_with_services']
        for key in schema['schema'].iterkeys():
            if key not in ignore_fields:
                template_fields.append(key)

        self.assertItemsEqual([x.encode('UTF8') for x in rh[1]['_template_fields']],
                              template_fields)

        datal = [{
            'name': 'host_002',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }, {
            'name': 'host_003',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }]

        requests.post(self.endpoint + '/host', json=datal, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[2]['name'], "host_002")
        self.assertEqual(rh[3]['name'], "host_003")

    def test_host_templates_updates(self):
        """
        Test when update a host template

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        data['_is_template'] = True
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")

        data = {
            'name': 'host_001',
            '_templates': [rh[0]['_id']],
            'realm': self.realm_all
        }
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_command'], rc[0]['_id'])

        datap = {'check_interval': 1}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh[1]['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh[1]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['check_interval'], 1)
        if 'check_interval' in rh[1]['_template_fields']:
            state = False
            self.assertTrue(state, 'check_interval does not be in _template_fields list')

        # update the template
        datap = {'initial_state': 'o'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh[0]['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh[0]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['initial_state'], "o")
        self.assertEqual(rh[1]['name'], "host_001")
        self.assertEqual(rh[1]['initial_state'], "o")
        if 'initial_state' not in rh[1]['_template_fields']:
            state = False
            self.assertTrue(state, 'initial_state must be in _template_fields list')

        # update the template name
        datap = {'name': 'testhost'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh[0]['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh[0]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "testhost")
        self.assertEqual(rh[1]['name'], "host_001")

    def test_service_templates(self):
        """
        Test service templates

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['name'] = 'host_001'
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
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
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping")

        data = {
            'host_name': rh[1]['_id'],
            '_templates': [rs[0]['_id']],
            '_realm': self.realm_all
        }
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping")
        self.assertEqual(rs[1]['name'], "ping")
        self.assertEqual(rs[1]['host_name'], rh[1]['_id'])

    def test_service_templates_updates(self):
        """
        Test when update service template

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['name'] = 'host_001'
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
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
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping")

        data = {
            'name': 'ping_test',
            'host_name': rh[1]['_id'],
            '_templates': [rs[0]['_id']],
            '_realm': self.realm_all
        }
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping")
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['host_name'], rh[1]['_id'])

        datap = {'check_interval': 1}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs[1]['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs[1]['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['check_interval'], 1)
        if 'check_interval' in rs[1]['_template_fields']:
            state = False
            self.assertTrue(state, 'check_interval does not be in _template_fields list')

        # update the template
        datap = {'initial_state': 'u'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs[0]['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs[0]['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['initial_state'], "u")
        self.assertEqual(rs[1]['name'], "ping_test")
        self.assertEqual(rs[1]['initial_state'], "u")
        if 'initial_state' not in rs[1]['_template_fields']:
            state = False
            self.assertTrue(state, 'initial_state must be in _template_fields list')

        # update the template name
        datap = {'name': 'ping2'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs[0]['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs[0]['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping2")
        self.assertEqual(rs[1]['name'], "ping_test")

    def test_host_services_template(self):
        """
        Test when use and add / modify / delete (host + service) template

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        data = json.loads(open('cfg/command_http.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        data = json.loads(open('cfg/command_https.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        data = json.loads(open('cfg/command_ssh.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(len(rc), 4)
        self.assertEqual(rc[0]['name'], "ping")
        self.assertEqual(rc[1]['name'], "http")
        self.assertEqual(rc[2]['name'], "https")
        self.assertEqual(rc[3]['name'], "ssh")

        # Add host templates
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        data['name'] = 'template_standard_linux'
        data['_is_template'] = True
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        data['name'] = 'template_web'
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(len(rh), 2)
        self.assertEqual(rh[0]['name'], "template_standard_linux")
        self.assertEqual(rh[1]['name'], "template_web")

        # Add services templates
        data = {
            'name': 'ping',
            'host_name': rh[0]['_id'],
            'check_command': rc[0]['_id'],
            'business_impact': 4,
            '_is_template': True,
            '_realm': self.realm_all
        }
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        data['name'] = 'ssh'
        data['check_command'] = rc[3]['_id']
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        data['name'] = 'http'
        data['host_name'] = rh[1]['_id']
        data['check_command'] = rc[1]['_id']
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        data['name'] = 'https'
        data['check_command'] = rc[2]['_id']
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(len(rs), 4)
        self.assertEqual(rs[0]['name'], "ping")
        self.assertEqual(rs[1]['name'], "ssh")
        self.assertEqual(rs[2]['name'], "http")
        self.assertEqual(rs[3]['name'], "https")

        # add a host with host template + allow service templates
        data = {
            'name': 'host_001',
            '_templates': [rh[0]['_id'], rh[1]['_id']],
            '_templates_with_services': True,
            'realm': self.realm_all
        }
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[2]['name'], "host_001")
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(len(rs), 8)
        self.assertEqual(rs[4]['name'], "http")
        self.assertEqual(rs[5]['_is_template'], False)
        self.assertEqual(rs[5]['name'], "ping")
        self.assertEqual(rs[6]['name'], "ssh")
        self.assertEqual(rs[7]['name'], "https")

        # Now update a service template
        data = {'name': 'ping2'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs[0]['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs[0]['_id'], json=data,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping2")
        self.assertEqual(rs[5]['name'], "ping2")

        # Now remove the template template_web of the host
        data = {'_templates': [rh[0]['_id']]}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh[2]['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh[2]['_id'], json=data, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(len(rs), 6)
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[2]['_templates'], [rh[0]['_id']])

        # Now re-add the template template_web of host
        data = {'_templates': [rh[0]['_id'], rh[1]['_id']]}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh[2]['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh[2]['_id'], json=data,
                       headers=headers_patch, auth=self.auth)

        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[2]['_templates'], [rh[0]['_id'], rh[1]['_id']])
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(len(rs), 8)

        # Now add a new template service
        data = {
            'name': 'ssh_new_method',
            'host_name': rh[0]['_id'],
            'check_command': rc[0]['_id'],
            'business_impact': 4,
            '_is_template': True,
            '_templates_from_host_template': True,
            '_realm': self.realm_all
        }
        responsep = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                  auth=self.auth)
        ret_new = responsep.json()
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']

        self.assertEqual(len(rs), 10)
        self.assertEqual(rs[9]['_templates'][0], ret_new['_id'])
        self.assertFalse(rs[9]['_is_template'])
        self.assertEqual(rs[8]['_templates'], [])
        self.assertTrue(rs[8]['_is_template'])

        # Now delete a template service
        headers_delete = {
            'Content-Type': 'application/json',
            'If-Match': ret_new['_etag']
        }
        requests.delete(self.endpoint + '/service/' + ret_new['_id'], headers=headers_delete,
                        auth=self.auth)
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        service_name = []
        for serv in resp['_items']:
            service_name.append(serv['name'])
        self.assertEqual(len(resp['_items']), 8)
        self.assertEqual(['ping2', 'ssh', 'http', 'https', 'ping2', 'ssh', 'http', 'https'],
                         service_name)
