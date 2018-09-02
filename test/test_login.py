#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module test login to backend
"""

from __future__ import print_function
import os
import time
import shlex
import subprocess
import requests
import unittest2


class Test_Login(unittest2.TestCase):
    """
    The class test login to backend
    """

    @classmethod
    def setUpClass(cls):
        """
        This method:
          * delete mongodb database
          * start the backend with uwsgi

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

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_0(self):
        """
        Test login to have token and parameter to force generate a new token

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin'}
        # get token
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']

        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert resp['token']
        token = resp['token']

        params['action'] = 'generate'
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert token != resp['token']
