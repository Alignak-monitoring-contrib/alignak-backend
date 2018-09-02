#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test checks the overall state update
"""

import os
import json
import time
import shlex
import subprocess
import copy
import requests
import unittest2
from alignak_backend.livesynthesis import Livesynthesis


class TestOverallState(unittest2.TestCase):
    """This class test the overall stat update"""

    @classmethod
    def setUpClass(cls):
        """This method:
          * deletes mongodb database
          * starts the backend with uwsgi
          * logs in the backend and get the token
          * gets the realm

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

        # get realms
        response = requests.get(cls.endpoint + '/realm',
                                auth=cls.auth)
        resp = response.json()
        cls.realm_all = resp['_items'][0]['_id']

    @classmethod
    def tearDownClass(cls):
        """Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    @classmethod
    def setUp(cls):
        """Delete resources in backend

        :return: None
        """
        for resource in ['host', 'service', 'command', 'livesynthesis']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_host_customs(self):  # pylint: disable=too-many-locals
        """Test host customs variables update

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}

        # ---
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command exists in the backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 3)
        rc = resp['_items']

        # ---
        # Add an host with some data
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[2]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        # Some customs
        data['customs'] = {
            'host_var1': 'value'
        }
        response = requests.post(self.endpoint + '/host',
                                 json=data, headers=headers, auth=self.auth)
        response = response.json()
        response = requests.get(self.endpoint + '/host/' + response['_id'],
                                params=sort_id, auth=self.auth)
        my_host = response.json()
        self.assertEqual(my_host['customs'], {'host_var1': 'value'})
        host_updated = my_host['_updated']

        # Add a service with some data
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = my_host['_id']
        data['check_command'] = rc[2]['_id']
        data['_realm'] = self.realm_all
        # Some customs
        data['customs'] = {
            'service_var1': 'value'
        }
        response = requests.post(self.endpoint + '/service', json=data,
                                 headers=headers, auth=self.auth)
        response = response.json()
        response = requests.get(self.endpoint + '/service/' + response['_id'],
                                params=sort_id, auth=self.auth)
        my_service = response.json()
        self.assertEqual(my_service['customs'], {'service_var1': 'value'})
        service_updated = my_service['_updated']

        # Update customs for the host
        time.sleep(0.1)
        data = {
            'customs': {'host_var1': 'new value', 'host_var2': 'new variable'}
        }
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': my_host['_etag']
        }
        requests.patch(self.endpoint + '/host/' + my_host['_id'], json=data,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/host/' + my_host['_id'],
                                params=sort_id, auth=self.auth)
        my_host = response.json()
        # _updated did not changed
        new_updated = my_host['_updated']
        self.assertEqual(host_updated, new_updated)

        # Update customs for the service
        time.sleep(0.1)
        data = {
            'customs': {'service_var1': 'new value', 'service_var2': 'new variable'}
        }
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': my_service['_etag']
        }
        requests.patch(self.endpoint + '/service/' + my_service['_id'], json=data,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/service/' + my_service['_id'],
                                params=sort_id, auth=self.auth)
        my_service = response.json()
        # _updated did not changed
        new_updated = my_service['_updated']
        self.assertEqual(service_updated, new_updated)
