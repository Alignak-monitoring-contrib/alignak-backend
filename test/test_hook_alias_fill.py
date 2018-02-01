#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify the alias filled when not defined
"""

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2
from alignak_backend.models.host import get_schema as host_schema
from alignak_backend.models.user import get_schema as user_schema


class TestHookAliasFill(unittest2.TestCase):
    """
    This class test the hooks used to fill alias when not defined
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

        # Login as admin
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin', 'action': 'generate'}
        response = requests.post(cls.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth = requests.auth.HTTPBasicAuth(cls.token, '')

        # Get user admin
        response = requests.get(cls.endpoint + '/user', auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]

        # Get default realm
        response = requests.get(cls.endpoint + '/realm', auth=cls.auth,
                                params={'where': json.dumps({'name': 'All'})})
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
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis', 'user',
                         'userrestrictrole']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_host_notfill_alias(self):
        """Create a new host with alias not defined

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
        self.assertEqual(len(resp['_items']), 3)
        rc = resp['_items']

        data = json.loads(open('cfg/host_srv001.json').read())
        if 'alias' in data:
            del data['alias']
        data['check_command'] = rc[2]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()

        # Get the newly created host
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        host = response.json()
        self.assertEqual(host['name'], "srv001")
        self.assertEqual(host['_realm'], self.realm_all)
        self.assertEqual(host['alias'], 'srv001')

    def test_host_fill_alias(self):
        """Create a new host with alias not defined

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
        self.assertEqual(len(resp['_items']), 3)
        rc = resp['_items']

        data = json.loads(open('cfg/host_srv001.json').read())
        data['alias'] = 'test'
        data['check_command'] = rc[2]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()

        # Get the newly created host
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        host = response.json()
        self.assertEqual(host['name'], "srv001")
        self.assertEqual(host['_realm'], self.realm_all)
        self.assertEqual(host['alias'], 'test')
