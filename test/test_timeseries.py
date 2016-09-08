#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check preparation of timeseries
"""

import time
import os
import shlex
import subprocess
import requests
import unittest2
from bson.objectid import ObjectId
from alignak_backend.timeseries import Timeseries


class TestTimeseries(unittest2.TestCase):
    """
    This class test timeseries preparation
    """

    maxDiff = None

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
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
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
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_prepare_data(self):
        """
        Prepare timeseries from a web perfdata

        :return: None
        """
        item = {
            'host': 'srv001',
            'service': 'check_xxx',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'NGINX OK -  0.161 sec. response time, Active: 25 (Writing: 3 Reading: 0 '
                      'Waiting: 22) ReqPerSec: 58.000 ConnPerSec: 1.200 ReqPerConn: 4.466',
            'long_output': '',
            'perf_data': 'Writing=3;;;; Reading=0;;;; Waiting=22;;;; Active=25;1000;2000;; '
                         'ReqPerSec=58.000000;100;200;; ConnPerSec=1.200000;200;300;; '
                         'ReqPerConn=4.465602;;;;',
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'ReqPerConn',
                    'value': {
                        'name': 'ReqPerConn',
                        'min': None,
                        'max': None,
                        'value': 4.465602,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'Writing',
                    'value': {
                        'name': 'Writing',
                        'min': None,
                        'max': None,
                        'value': 3,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'Waiting',
                    'value': {
                        'name': 'Waiting',
                        'min': None,
                        'max': None,
                        'value': 22,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                },
                {
                    'name': 'ConnPerSec',
                    'value': {
                        'name': 'ConnPerSec',
                        'min': None,
                        'max': None,
                        'value': 1.2,
                        'warning': 200,
                        'critical': 300,
                        'uom': ''
                    }
                },
                {
                    'name': 'Active',
                    'value': {
                        'name': 'Active',
                        'min': None,
                        'max': None,
                        'value': 25,
                        'warning': 1000,
                        'critical': 2000,
                        'uom': ''
                    }
                },
                {
                    'name': 'ReqPerSec',
                    'value': {
                        'name': 'ReqPerSec',
                        'min': None,
                        'max': None,
                        'value': 58,
                        'warning': 100,
                        'critical': 200,
                        'uom': ''
                    }
                },
                {
                    'name': 'Reading',
                    'value': {
                        'name': 'Reading',
                        'min': None,
                        'max': None,
                        'value': 0,
                        'warning': None,
                        'critical': None,
                        'uom': ''
                    }
                }
            ]
        }
        self.assertItemsEqual(reference, ret)

    def test_generate_realm_prefix(self):
        """
        Test generate realm prefix when have many levels

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        data = {
            'name': 'realm A',
            '_parent': self.realm_all
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_a = resp['_id']

        data = {
            'name': 'realm B',
            '_parent': self.realm_all
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_b = resp['_id']

        data = {
            'name': 'realm A1',
            '_parent': realm_a
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_a1 = resp['_id']

        from alignak_backend.app import app
        with app.test_request_context():
            prefix = Timeseries.get_realms_prefix(ObjectId(self.realm_all))
            self.assertEqual(prefix, 'All')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_a))
            self.assertEqual(prefix, 'All.realm A')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_b))
            self.assertEqual(prefix, 'All.realm B')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_a1))
            self.assertEqual(prefix, 'All.realm A.realm A1')
