#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the userrestrict (uipref)
"""

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestUserManagement(unittest2.TestCase):
    """
    This class tests the backend users management
    """

    @classmethod
    def setUpClass(cls):
        """
        This method:
          * deletes former mongodb database
          * starts the backend with uwsgi
          * logs in the backend and get the token
          * gets the default realm

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
        # get user admin
        response = requests.get(cls.endpoint + '/user',
                                auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]

        # get realms
        response = requests.get(cls.endpoint + '/realm',
                                auth=cls.auth)
        resp = response.json()
        cls.realmAll_id = resp['_items'][0]['_id']

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_user_creation(self):
        """Create user with minimum data.
        User has Never timeperiods for notifications of hosts and services

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        response = requests.get(self.endpoint + '/timeperiod',
                                params={'where': json.dumps({'name': 'Never'})}, auth=self.auth)
        tps = response.json()
        never = tps['_items'][0]['_id']

        # Add a new user with minimum necessary data
        data = {
            'name': 'user0',
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user1_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user0'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user1 = response.json()
        user1 = user1['_items'][0]
        assert user1['_id'] == user1_id
        assert 'token' in user1
        assert user1['token'] != ''
        assert user1['host_notification_period'] == never
        assert user1['service_notification_period'] == never
        assert user1['skill_level'] == 0

        # Get the default created user rights
        params = {'where': json.dumps({'user': user1_id})}
        response = requests.get(self.endpoint + '/userrestrictrole', params=params, auth=self.auth)
        urr = response.json()
        urr = urr['_items'][0]
        assert urr['user'] == user1_id
        assert urr['resource'] == '*'
        assert urr['crud'] == ['read']
        assert urr['realm'] == user1['_realm']
        assert urr['sub_realm'] == user1['_sub_realm']

        # Try to login with user account
        params = {'username': 'user1', 'password': ''}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert resp['_status'] == 'ERR'
        assert resp['_error']['code'] == 401
        assert resp['_error']['message'] == 'Username and password must be provided ' \
                                            'as credentials for login.'

        # Indeed the backend sets a defaut NOPASSWORDSET password
        params = {'username': 'user0', 'password': 'NOPASSWORDSET'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert 'token' in resp
        assert resp['token'] != ''

    def test_token_on_creation_and_login(self):
        """Create user with no password.
        Login is authorized with the default password
        User token is automatically defined on login

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a new user with minimum necessary data
        data = {
            'name': 'user1',
            'host_notification_period': self.user_admin['host_notification_period'],
            'service_notification_period': self.user_admin['service_notification_period'],
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user1_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user1'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user1 = response.json()
        user1 = user1['_items'][0]
        assert user1['_id'] == user1_id
        assert 'token' in user1
        assert user1['token'] != ''

        # Try to login with user account
        params = {'username': 'user1', 'password': ''}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert resp['_status'] == 'ERR'
        assert resp['_error']['code'] == 401
        assert resp['_error']['message'] == 'Username and password must be provided ' \
                                            'as credentials for login.'

        # Indeed the backend sets a defaut NOPASSWORDSET password
        params = {'username': 'user1', 'password': 'NOPASSWORDSET'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        assert 'token' in resp
        assert resp['token'] != ''

    def test_token_on_update(self):
        """Create user with no password.
        User token is automatically defined on update

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a new user with minimum necessary data
        data = {
            'name': 'user2',
            'host_notification_period': self.user_admin['host_notification_period'],
            'service_notification_period': self.user_admin['service_notification_period'],
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user2_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user2'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user2 = response.json()
        user2 = user2['_items'][0]
        assert user2['_id'] == user2_id
        assert 'token' in user2
        # No defined token
        assert user2['token'] != ''
        first_token = user2['token']

        # Update the user with a new token
        datap = {'token': ''}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': user2['_etag']
        }
        response = requests.patch(self.endpoint + '/user/' + user2['_id'],
                                  json=datap, headers=headers_patch, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'

        # Get updated user
        params = {'where': json.dumps({'name': 'user2'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user2 = response.json()
        user2 = user2['_items'][0]
        assert user2['_id'] == user2_id
        assert 'token' in user2
        # New defined token
        assert user2['token'] != ''
        assert user2['token'] != first_token

    def test_token_on_create(self):
        """Create user with empty token.
        User token is automatically defined on creation

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a new user with minimum necessary data
        data = {
            'name': 'user3', 'token': '',
            'host_notification_period': self.user_admin['host_notification_period'],
            'service_notification_period': self.user_admin['service_notification_period'],
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user3_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user3'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user3 = response.json()
        user3 = user3['_items'][0]
        assert user3['_id'] == user3_id
        assert 'token' in user3
        # Defined token
        assert user3['token'] != ''

    def test_skill_level(self):
        """Create user with empty token.
        User token is automatically defined on creation

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a new user with minimum necessary data
        data = {'name': 'user4', '_realm': self.realmAll_id}
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user4_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user4'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user4 = response.json()
        user4 = user4['_items'][0]
        assert user4['_id'] == user4_id
        # Default user skill is set as beginner
        assert user4['skill_level'] == 0

        # ---
        # Add a new user with a specif skill level
        data = {'name': 'user5', '_realm': self.realmAll_id, 'skill_level': 1}
        response = requests.post(self.endpoint + '/user',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        assert resp['_status'] == 'OK'
        assert '_id' in resp
        user5_id = resp['_id']

        # Get newly created user
        params = {'where': json.dumps({'name': 'user5'})}
        response = requests.get(self.endpoint + '/user', params=params, auth=self.auth)
        user5 = response.json()
        user5 = user5['_items'][0]
        assert user5['_id'] == user5_id
        # Default user skill is set as beginner
        assert user5['skill_level'] == 1
