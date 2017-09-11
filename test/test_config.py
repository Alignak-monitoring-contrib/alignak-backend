#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test checks backend configuration endpoint
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


class TestConfig(unittest2.TestCase):
    """This class test backend configuration endpoint"""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        """This method:
          * deletes mongodb database
          * starts the backend with uwsgi
          * logs in the backend and get the token
          * gets the default realm and admn user

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

    def test_config_endpoint(self):
        """Get backend configuration

        :return: None
        """
        # Get backend configuration
        response = requests.get(self.endpoint + '/backendconfig')
        resp = response.json()
        assert resp == {u'PAGINATION_DEFAULT': 25, u'PAGINATION_LIMIT': 50}
