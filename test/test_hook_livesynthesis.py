#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify the different hooks used in the backend to update livesynthesis
"""

import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestHookLivesynthesis(unittest2.TestCase):
    """
    This class test the hooks used to update livesynthesis resource
    """

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
        Delete resources in backend

        :return: None
        """
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_add_host(self):
        """
        Test livesynthesis when add a host

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

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if livesynthesis right created
        response = requests.get(self.endpoint + '/livesynthesis', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['hosts_total'], 1)
        self.assertEqual(r[0]['hosts_up_hard'], 0)
        self.assertEqual(r[0]['hosts_up_soft'], 0)
        self.assertEqual(r[0]['hosts_down_hard'], 0)
        self.assertEqual(r[0]['hosts_down_soft'], 0)
        self.assertEqual(r[0]['hosts_unreachable_hard'], 1)
        self.assertEqual(r[0]['hosts_unreachable_soft'], 0)
        self.assertEqual(r[0]['hosts_acknowledged'], 0)
        self.assertEqual(r[0]['services_total'], 0)
        self.assertEqual(r[0]['services_ok_hard'], 0)
        self.assertEqual(r[0]['services_ok_soft'], 0)
        self.assertEqual(r[0]['services_warning_hard'], 0)
        self.assertEqual(r[0]['services_warning_soft'], 0)
        self.assertEqual(r[0]['services_critical_hard'], 0)
        self.assertEqual(r[0]['services_critical_soft'], 0)
        self.assertEqual(r[0]['services_unknown_hard'], 0)
        self.assertEqual(r[0]['services_unknown_soft'], 0)

    def test_add_service(self):
        """
        Test livesynthesis when add a service

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

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host_name'] = rh[0]['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

        # Check if livesynthesis right created
        response = requests.get(self.endpoint + '/livesynthesis', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['hosts_total'], 1)
        self.assertEqual(r[0]['hosts_up_hard'], 0)
        self.assertEqual(r[0]['hosts_up_soft'], 0)
        self.assertEqual(r[0]['hosts_down_hard'], 0)
        self.assertEqual(r[0]['hosts_down_soft'], 0)
        self.assertEqual(r[0]['hosts_unreachable_hard'], 1)
        self.assertEqual(r[0]['hosts_unreachable_soft'], 0)
        self.assertEqual(r[0]['hosts_acknowledged'], 0)
        self.assertEqual(r[0]['services_total'], 1)
        self.assertEqual(r[0]['services_ok_hard'], 1)
        self.assertEqual(r[0]['services_ok_soft'], 0)
        self.assertEqual(r[0]['services_warning_hard'], 0)
        self.assertEqual(r[0]['services_warning_soft'], 0)
        self.assertEqual(r[0]['services_critical_hard'], 0)
        self.assertEqual(r[0]['services_critical_soft'], 0)
        self.assertEqual(r[0]['services_unknown_hard'], 0)
        self.assertEqual(r[0]['services_unknown_soft'], 0)
