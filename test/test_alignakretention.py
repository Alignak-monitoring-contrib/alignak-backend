#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify the alignakretention part
"""

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2
from alignak_backend.models.alignakretention import get_schema as retention_schema
from alignak_backend.models.user import get_schema as user_schema


class TestRetention(unittest2.TestCase):
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
        # Set test mode for Alignak backend
        os.environ['ALIGNAK_BACKEND_TEST'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-templates-test'
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

        # get realms
        response = requests.get(cls.endpoint + '/realm',
                                auth=cls.auth)
        resp = response.json()
        cls.realm_all = resp['_items'][0]['_id']

        # Get admin user
        response = requests.get(cls.endpoint + '/user', {"name": "admin"}, auth=cls.auth)
        resp = response.json()
        cls.user_admin_id = resp['_items'][0]['_id']
        cls.user_admin = resp['_items'][0]

        # add user2
        # Add a new user with minimum necessary data
        data = {
            'name': 'user2', 'token': '', 'password': 'user2',
            'host_notification_period': cls.user_admin['host_notification_period'],
            'service_notification_period': cls.user_admin['service_notification_period'],
            '_realm': cls.realm_all
        }
        response = requests.post(cls.endpoint + '/user',
                                 json=data, headers=headers, auth=cls.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        cls.user2_id = resp['_id']

        params = {'username': 'user2', 'password': 'user2', 'action': 'generate'}
        # get token
        response = requests.post(cls.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth2 = requests.auth.HTTPBasicAuth(cls.token, '')

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
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis', 'user']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_retention(self):
        """Test add a host used a template

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Test post data in retention with user 'admin'
        data = {
            'host': 'srv001',
            'latency': 0,
            'last_state_type': 'HARD',
            'state': 'UP',
            'last_chk': 0,
        }
        response = requests.post(
            self.endpoint + '/alignakretention', json=data, headers=headers, auth=self.auth
        )
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')

        response = requests.get(self.endpoint + '/alignakretention', auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(len(re), 1)

        # test user 'user2' can't list data of user 'admin'
        response = requests.get(self.endpoint + '/alignakretention', auth=self.auth2)
        resp = response.json()
        re2 = resp['_items']
        self.assertEqual(len(re2), 0)

        # test user 'user2' don't have access to data of user 'admin'
        response = requests.get(self.endpoint + '/alignakretention/' + re[0]['_id'],
                                auth=self.auth2)
        resp = response.json()
        self.assertEqual(resp['_status'], 'ERR', resp)

        # test put data in retention with user 'admin'
        data['latency'] = 3
        headers_put = {
            'Content-Type': 'application/json',
            'If-Match': re[0]['_etag']
        }
        response = requests.put(
            self.endpoint + '/alignakretention/' + re[0]['_id'], json=data, headers=headers_put,
            auth=self.auth
        )
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')
        response = requests.get(self.endpoint + '/alignakretention', auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(re[0]['latency'], 3)

        # test user 'user2' can't put data on data of user 'admin' because _etag not right
        data['latency'] = 4
        headers_put = {
            'Content-Type': 'application/json',
            'If-Match': 'roifetgiuvetigu'
        }
        response = requests.put(
            self.endpoint + '/alignakretention/' + re[0]['_id'], json=data, headers=headers_put,
            auth=self.auth2
        )
        assert response.status_code == 412

        # test user 'user2' can put data on data of user 'admin', but of course the user need have
        # the _id and the _etag
        data['latency'] = 4
        headers_put = {
            'Content-Type': 'application/json',
            'If-Match': re[0]['_etag']
        }
        response = requests.put(
            self.endpoint + '/alignakretention/' + re[0]['_id'], json=data, headers=headers_put,
            auth=self.auth2
        )
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')
