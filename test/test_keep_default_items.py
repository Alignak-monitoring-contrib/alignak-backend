#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the delete not works on default items (timeperiod 24x7 for example)
"""

from __future__ import print_function
import os
import json
import time
from calendar import timegm
from datetime import datetime, timedelta
import shlex
import subprocess
import copy
import requests
import unittest2


class TestKeppDefaultItems(unittest2.TestCase):
    """
    This class test delete items but not the default items created when start backend first time
    """

    @classmethod
    def setUpClass(cls):
        """
        This method:
          * delete mongodb database
          * start the backend with uwsgi
          * log in the backend and get the token
          * get the hostgroup

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

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_delete_timeperiods(self):
        """Test delete timeperiods
        We always keep the 2 timeperiods:

         * 24x7
         * Never

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}

        # add some timeperiods
        data = {
            'name': 'tp001',
            '_realm': self.realm_all
        }
        response = requests.post(self.endpoint + '/timeperiod', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # delete all
        response = requests.delete(self.endpoint + '/timeperiod', auth=self.auth)
        self.assertEqual('OK', resp['_status'], response)

        # check we have 2 timeperiods, the default 24x7 and Never
        response = requests.get(self.endpoint + '/timeperiod', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][0]['name'], '24x7')
        self.assertEqual(resp['_items'][1]['name'], 'Never')

        # add new timeperiod
        data = {
            'name': 'tp002',
            '_realm': self.realm_all
        }
        response = requests.post(self.endpoint + '/timeperiod', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # get all timeperiods
        response = requests.get(self.endpoint + '/timeperiod', params=sort_id, auth=self.auth)
        resp = response.json()
        rt = resp['_items']

        # try delete timeperiod tp002
        headers_delete = {
            'Content-Type': 'application/json',
            'If-Match': rt[2]['_etag']
        }
        response = requests.delete(self.endpoint + '/timeperiod/' + rt[2]['_id'],
                                   headers=headers_delete, auth=self.auth)
        self.assertEqual(204, response.status_code, response)

        response = requests.get(self.endpoint + '/timeperiod', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        rt = resp['_items']
        self.assertEqual(resp['_items'][0]['name'], '24x7')
        self.assertEqual(resp['_items'][1]['name'], 'Never')

        # try delete timeperiod 24x7
        headers_delete = {
            'Content-Type': 'application/json',
            'If-Match': rt[0]['_etag']
        }
        response = requests.delete(self.endpoint + '/timeperiod/' + rt[0]['_id'],
                                   headers=headers_delete, auth=self.auth)
        self.assertEqual(412, response.status_code, response)

        response = requests.get(self.endpoint + '/timeperiod', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][0]['name'], '24x7')
        self.assertEqual(resp['_items'][1]['name'], 'Never')

    def test_delete_user(self):
        """Test delete user
        We always keep the admin user and the currently logged-in user

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}

        # add some users
        data = {
            'name': 'user1',
            '_realm': self.realm_all
        }
        response = requests.post(self.endpoint + '/user', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # add some users
        data = {
            'name': 'user2',
            '_realm': self.realm_all
        }
        response = requests.post(self.endpoint + '/user', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # delete all users
        response = requests.delete(self.endpoint + '/user', auth=self.auth)
        self.assertEqual('OK', resp['_status'], response)

        # check we have 1 user, the admin user
        response = requests.get(self.endpoint + '/user', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 1)
        self.assertEqual(resp['_items'][0]['name'], 'admin')

    def test_token_on_creation_and_login(self):
        """Create user with no password.
        Login is authorized with the default password
        User token is automatically defined on login

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a new user with minimum necessary data
        data = {
            'name': 'other_user',
            '_realm': self.realm_all
        }
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        myself_id = resp['_id']
        myself_etag = resp['_etag']

        # check we have 2 user, the admin user and the new one
        response = requests.get(self.endpoint + '/user', auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][0]['name'], 'admin')
        self.assertEqual(resp['_items'][1]['name'], 'other_user')

        # Login with the new user account
        params = {'username': 'other_user', 'password': 'NOPASSWORDSET'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert 'token' in resp
        assert resp['token'] != ''
        auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        # Try to delete myself
        headers_delete = {'Content-Type': 'application/json', 'If-Match': myself_etag}
        response = requests.delete(self.endpoint + '/user/' + myself_id,
                                   auth=auth, headers=headers_delete)
        # Refused !
        assert response.status_code == 412

        # We still have 2 users!
        response = requests.get(self.endpoint + '/user', auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][0]['name'], 'admin')
        self.assertEqual(resp['_items'][1]['name'], 'other_user')
