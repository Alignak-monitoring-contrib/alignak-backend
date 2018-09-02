#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module tests the hostescalation features
"""

from __future__ import print_function

import os
import json
import shlex
import subprocess
import time
from calendar import timegm
from datetime import datetime

import requests
import unittest2


class TestHostescalation(unittest2.TestCase):
    """This class tests the hostescalation features"""

    @classmethod
    def setUpClass(cls):
        """This method:
          * deletes mongodb database
          * starts the backend with uwsgi
          * logs in the backend as admin
          * creates resources in the backend

        :return: None
        """
        # Set test mode for Alignak backend
        os.environ['ALIGNAK_BACKEND_TEST'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = './cfg/settings/settings.json'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignak_backend.app:app',
                                  '--socket', '0.0.0.0:5000',
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

        # Get default realm
        response = requests.get(cls.endpoint + '/realm', auth=cls.auth)
        resp = response.json()
        cls.realm_all = resp['_items'][0]['_id']

        # Get admin user
        response = requests.get(cls.endpoint + '/user', {"name": "admin"}, auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]['_id']

        # Get Always TP
        response = requests.get(cls.endpoint + '/timeperiod', {"name": "24x7"}, auth=cls.auth)
        resp = response.json()
        cls.always = resp['_items'][0]['_id']

        headers = {'Content-Type': 'application/json'}

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = cls.realm_all
        requests.post(cls.endpoint + '/command', json=data, headers=headers, auth=cls.auth)
        response = requests.get(cls.endpoint + '/command', auth=cls.auth)
        resp = response.json()
        rc = resp['_items']

        # Add some hosts and services
        cls.servers = []
        cls.ws = []
        data = {
            'name': 'server-1',
            'check_command': rc[0]['_id'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        response = response.json()
        cls.servers.append(response['_id'])
        data = {
            'name': 'server-2',
            'check_command': rc[0]['_id'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        response = response.json()
        cls.servers.append(response['_id'])
        data = {
            'name': 'server-3',
            'check_command': rc[0]['_id'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        response = response.json()
        cls.servers.append(response['_id'])
        data = {
            'name': 'ws-1',
            'check_command': rc[0]['_id'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        response = response.json()
        cls.ws.append(response['_id'])
        data = {
            'name': 'ws-2',
            'check_command': rc[0]['_id'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        response = response.json()
        cls.ws.append(response['_id'])

        # Add services for each host
        for server in cls.servers:
            data = {
                'name': 'check_host_alive',
                'host': server, 'check_command': rc[0]['_id'], '_realm': cls.realm_all
            }
            requests.post(cls.endpoint + '/service', json=data, headers=headers, auth=cls.auth)
            data = {
                'name': 'load',
                'host': server, 'check_command': rc[0]['_id'], '_realm': cls.realm_all
            }
            requests.post(cls.endpoint + '/service', json=data, headers=headers, auth=cls.auth)
            data = {
                'name': 'memory',
                'host': server, 'check_command': rc[0]['_id'], '_realm': cls.realm_all
            }
            requests.post(cls.endpoint + '/service', json=data, headers=headers, auth=cls.auth)

        for ws in cls.ws:
            data = {
                'name': 'check_host_alive',
                'host': ws, 'check_command': rc[0]['_id'], '_realm': cls.realm_all
            }
            requests.post(cls.endpoint + '/service', json=data, headers=headers, auth=cls.auth)
            data = {
                'name': 'load',
                'host': ws, 'check_command': rc[0]['_id'], '_realm': cls.realm_all
            }
            requests.post(cls.endpoint + '/service', json=data, headers=headers, auth=cls.auth)

        # Add some hosts groups
        data = {
            'name': 'hg_servers',
            'hosts': cls.servers,
            '_realm': cls.realm_all
        }
        requests.post(cls.endpoint + '/hostgroup', json=data, headers=headers, auth=cls.auth)
        data = {
            'name': 'hg_ws',
            'hosts': cls.ws,
            '_realm': cls.realm_all
        }
        requests.post(cls.endpoint + '/hostgroup', json=data, headers=headers, auth=cls.auth)

    @classmethod
    def tearDownClass(cls):
        """Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    @classmethod
    def setUp(cls):
        # pylint: disable=len-as-condition
        """Get resources from the backend

        :return: None
        """
        # No existing services escalations
        response = requests.get(cls.endpoint + '/hostescalation', auth=cls.auth)
        resp = response.json()
        cls.re = resp['_items']
        assert len(cls.re) == 0

        # Get hosts in the backend
        response = requests.get(cls.endpoint + '/host', params={'sort': 'name'}, auth=cls.auth)
        resp = response.json()
        cls.rh = resp['_items']
        assert len(cls.rh) == 6

        # Get hostgroups in the backend
        response = requests.get(cls.endpoint + '/hostgroup', params={'sort': 'name'}, auth=cls.auth)
        resp = response.json()
        cls.rhg = resp['_items']
        assert len(cls.rhg) == 3

        # Get services in the backend
        response = requests.get(cls.endpoint + '/service', params={'sort': 'name'}, auth=cls.auth)
        resp = response.json()
        cls.rs = resp['_items']
        assert len(cls.rs) == 13

    @classmethod
    def tearDown(cls):
        """Delete resources in the backend

        :return: None
        """
        for resource in ['hostescalation']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_he_add_single(self):
        # pylint: disable=too-many-locals
        """Add a host escalation for a single host

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # -------------------------------------------
        # Add a host escalation for an host - minimum mandatory fields
        data = {
            'name': 'my_escalation',
            'hosts': [self.rh[0]['_id']],
            '_realm': self.realm_all,
            'users': [],
            'usergroups': []
        }
        response = requests.post(self.endpoint + '/hostescalation', json=data,
                                 headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')

        # Get hosts escalations
        response = requests.get(self.endpoint + '/hostescalation', auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1
        assert resp['_items'][0]['hosts'] == [self.rh[0]['_id']]
        assert 'hostgroups' not in resp['_items'][0]
        assert resp['_items'][0]['_realm'] == self.realm_all
        assert resp['_items'][0]['_sub_realm'] is True
        assert resp['_items'][0]['first_notification_time'] == 60
        assert resp['_items'][0]['last_notification_time'] == 240
        assert resp['_items'][0]['notification_interval'] == 60
        assert resp['_items'][0]['escalation_options'] == ['d', 'x', 'r']
        # Default escalation_period was set by the backend
        assert resp['_items'][0]['escalation_period'] == self.always
        # No default users / usergroups
        assert resp['_items'][0]['users'] == []
        assert resp['_items'][0]['usergroups'] == []

    def test_he_add_several(self):
        # pylint: disable=too-many-locals
        """Add a host escalation for several hosts

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # -------------------------------------------
        # Add a service escalation for several services
        data = {
            'name': 'my_escalation',
            'hosts': [
                self.rh[0]['_id'], self.rh[1]['_id'], self.rh[2]['_id'],
                self.rh[3]['_id'], self.rh[4]['_id']
            ],
            '_realm': self.realm_all,
            'users': [],
            'usergroups': []
        }
        response = requests.post(self.endpoint + '/hostescalation', json=data,
                                 headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')

        # Get hosts escalations
        response = requests.get(self.endpoint + '/hostescalation', auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1
        assert resp['_items'][0]['hosts'] == [
            self.rh[0]['_id'], self.rh[1]['_id'], self.rh[2]['_id'],
            self.rh[3]['_id'], self.rh[4]['_id']
        ]
        assert 'hostgroups' not in resp['_items'][0]
        assert resp['_items'][0]['_realm'] == self.realm_all
        assert resp['_items'][0]['_sub_realm'] is True
        assert resp['_items'][0]['first_notification_time'] == 60
        assert resp['_items'][0]['last_notification_time'] == 240
        assert resp['_items'][0]['notification_interval'] == 60
        assert resp['_items'][0]['escalation_options'] == ['d', 'x', 'r']
        # Default escalation_period was set by the backend
        assert resp['_items'][0]['escalation_period'] == self.always
        # No default users / usergroups
        assert resp['_items'][0]['users'] == []
        assert resp['_items'][0]['usergroups'] == []

    def test_he_add_hostgroups(self):
        # pylint: disable=too-many-locals
        """Add a host escalation for an hostgroup

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # -------------------------------------------
        # Add host escalation for an hostgroup
        data = {
            'name': 'my_escalation-3',
            'hosts': [],
            'hostgroups': [
                # This hostgroup has 3 hosts with some services
                self.rhg[1]['_id']
            ],
            '_realm': self.realm_all,
            'users': [],
            'usergroups': []
        }
        response = requests.post(self.endpoint + '/hostescalation', json=data,
                                 headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')

        # Get hosts escalations
        response = requests.get(self.endpoint + '/hostescalation',
                                params={'sort': '_id'}, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1

        assert resp['_items'][0]['hosts'] == []
        assert resp['_items'][0]['hostgroups'] == [self.rhg[1]['_id']]
        assert resp['_items'][0]['_realm'] == self.realm_all
        assert resp['_items'][0]['_sub_realm'] is True
        assert resp['_items'][0]['first_notification_time'] == 60
        assert resp['_items'][0]['last_notification_time'] == 240
        assert resp['_items'][0]['notification_interval'] == 60
        assert resp['_items'][0]['escalation_options'] == ['d', 'x', 'r']
        assert resp['_items'][0]['escalation_period'] == self.always
        assert resp['_items'][0]['users'] == []
        assert resp['_items'][0]['usergroups'] == []
