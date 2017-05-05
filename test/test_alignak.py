#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test checks alignak endpoint
"""

from __future__ import print_function
import os
import json
import time
import shlex
from random import randint
import subprocess
import requests
import requests_mock
import unittest2
from bson.objectid import ObjectId
from alignak_backend.grafana import Grafana


class TestAlignak(unittest2.TestCase):
    """This class tests alignak endpoint"""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        """This method:
          * delete mongodb database
          * start the backend with uwsgi
          * log in the backend and get the token
          * get the hostgroup

        :return: None
        """
        # Set test mode for Alignak backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignak_backend.app:app',
                                  '--socket', '0.0.0.0:5000',
                                  '--protocol=http', '--enable-threads', '--pidfile',
                                  '/tmp/uwsgi.pid', '--logto=/tmp/alignak_backend.log'])
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

        data = {"name": "All A", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_A = resp['_id']

        data = {"name": "All A1", "_parent": cls.realmAll_A}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_A1 = resp['_id']

        data = {"name": "All B", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_B = resp['_id']

        # Get admin user
        response = requests.get(cls.endpoint + '/user', {"name": "admin"}, auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]['_id']

    @classmethod
    def tearDownClass(cls):
        """Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)
        os.unlink("/tmp/alignak_backend.log")

    @classmethod
    def tearDown(cls):
        """Delete resources in backend

        :return: None
        """
        for resource in ['alignak']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_alignak(self):
        """Create and get alignak resources

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        # Add an Alignak configuration
        data = {
            'name': 'my_alignak',
            'alias': 'Test alignak configuration',
            'notifications_enabled': True,
            'flap_detection_enabled': False,
            '_TEST1': 'Test an extra non declared field',
            '_TEST2': 'One again - Test an extra non declared field',
            '_TEST3': 'And again - Test an extra non declared field',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/alignak', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Add the same Alignak configuration for another realm
        data = {
            'name': 'my_alignak',
            'alias': 'Test alignak configuration',
            'notifications_enabled': True,
            'flap_detection_enabled': False,
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/alignak', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        # Add some extra information for the same Alignak configuration for the same realm
        data = {
            'name': 'my_alignak',
            'alias': 'Test alignak configuration',
            'event_handlers_enabled': True,
            'passive_host_checks_enabled': False,
            'passive_service_checks_enabled': False,
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/alignak', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        _id = resp['_id']
        _etag = resp['_etag']
        _updated = resp['_updated']

        # Only update some fields, with a little delay...
        time.sleep(1)
        headers['If-Match'] = _etag
        data = {
            'name': 'my_alignak',
            'alias': 'New alias',
            'last_alive': 123456789,
            'last_command_check': 123456789,
            'last_log_rotation': 123456789
        }
        response = requests.patch(self.endpoint + '/alignak/%s' % _id, json=data,
                                  headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        assert _updated != resp['_updated']
        _id = resp['_id']
        _etag = resp['_etag']
        _updated = resp['_updated']

        # Only update some live running fields, with a little delay...
        time.sleep(1)
        headers['If-Match'] = _etag
        data = {
            'last_alive': 123456789,
            'last_command_check': 123456789,
            'last_log_rotation': 123456789
        }
        response = requests.patch(self.endpoint + '/alignak/%s' % _id, json=data,
                                  headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        assert _updated == resp['_updated']
