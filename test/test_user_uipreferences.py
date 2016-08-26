#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify not update _updated field when patch ui_preferences field
"""

import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestHookUserUiPreferences(unittest2.TestCase):
    """
    This class test _updated field not updated when patch ui_preferences field
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

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignakbackend:app',
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

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)


    def test_add_host(self):
        """
        Test the livestate hook to create a livestate resource when create a new host

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}

        response = requests.get(self.endpoint + '/user', params=sort_id, auth=self.auth)
        resp = response.json()
        ru = resp['_items']

        time.sleep(2)
        # Update user
        datap = {'address2': "my new address"}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': ru[0]['_etag']
        }
        requests.patch(self.endpoint + '/user/' + ru[0]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/user', params=sort_id, auth=self.auth)
        resp = response.json()
        ru2 = resp['_items']
        self.assertNotEqual(ru[0]['_updated'], ru2[0]['_updated'])
        ru = ru2

        time.sleep(2)
        # Update user
        datap = {'address2': "my new address bis", "ui_preferences": {"koin": "koin"}}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': ru[0]['_etag']
        }
        requests.patch(self.endpoint + '/user/' + ru[0]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/user', params=sort_id, auth=self.auth)
        resp = response.json()
        ru2 = resp['_items']
        self.assertNotEqual(ru[0]['_updated'], ru2[0]['_updated'])
        ru = ru2

        time.sleep(2)
        # Update user
        datap = {"ui_preferences": {"koin": "koin"}}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': ru[0]['_etag']
        }
        requests.patch(self.endpoint + '/user/' + ru[0]['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        response = requests.get(self.endpoint + '/user', params=sort_id, auth=self.auth)
        resp = response.json()
        ru2 = resp['_items']
        self.assertEqual(ru[0]['_updated'], ru2[0]['_updated'])
