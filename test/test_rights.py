#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check if rights of users in backend works
"""

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestRights(unittest2.TestCase):
    """
    This class test the rights in backend
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

        # Add realm
        data = {'name': 'Hoth', "_parent": cls.realmAll_id}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.hoth = resp['_id']

        data = {'name': 'Sluis', "_parent": cls.realmAll_id}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.sluis = resp['_id']

        data = {'name': 'Dagobah', "_parent": cls.sluis}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.dagobah = resp['_id']

        # Add users
        # User 1 - read right on Sluis realm and sub-realms
        data = {'name': 'user1', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.sluis}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user1_id = resp['_id']
        # data = {'user': resp['_id'], 'realm': cls.sluis, 'resource': 'command', 'crud': ['read'],
        #         'sub_realm': True}
        # requests.post(cls.endpoint + '/userrestrictrole', json=data, headers=headers,
        #               auth=cls.auth)

        # User 2 - read right on Hoth realm and sub-realms
        data = {'name': 'user2', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.hoth}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user2_id = resp['_id']
        # No more necessary: default is to get read right on user's realm
        # data = {'user': resp['_id'], 'realm': cls.hoth, 'resource': 'command', 'crud': ['read']}
        # requests.post(cls.endpoint + '/userrestrictrole', json=data, headers=headers,
        #               auth=cls.auth)

        # User 3 - read right on All realm and no sub-realms
        data = {'name': 'user3', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.realmAll_id, '_sub_realm': False}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user3_id = resp['_id']

        # User 4 - read right on Sluis realm and no sub-realms + custom right on command
        data = {'name': 'user4', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.sluis, '_sub_realm': False}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user4_id = resp['_id']
        data = {'user': resp['_id'], 'realm': cls.sluis, 'resource': 'command',
                'crud': ['custom']}
        requests.post(cls.endpoint + '/userrestrictrole', json=data, headers=headers,
                      auth=cls.auth)

        # User 5 - read right on Sluis realm and no sub-realms
        data = {'name': 'user5', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.sluis, '_sub_realm': False}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user5_id = resp['_id']
        # data = {'user': resp['_id'], 'realm': cls.sluis, 'resource': '*', 'crud': ['read']}
        # requests.post(cls.endpoint + '/userrestrictrole', json=data, headers=headers,
        #               auth=cls.auth)

        # User 6 - read right on Sluis realm and its sub realms
        data = {'name': 'user6', 'password': 'test', 'back_role_super_admin': False,
                '_realm': cls.sluis, '_sub_realm': True}
        response = requests.post(cls.endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.user6_id = resp['_id']
        # data = {'user': resp['_id'], 'realm': cls.sluis, 'resource': '*', 'crud': ['read'],
        #         'sub_realm': True}
        # requests.post(cls.endpoint + '/userrestrictrole', json=data, headers=headers,
        #               auth=cls.auth)

    @classmethod
    def tearDownClass(cls):
        """
        Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        time.sleep(2)

    def test_roles(self):
        """Test roles for different users to see if they get the right commands

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_users_read'] = [self.user1_id]
        data['_realm'] = self.realmAll_id
        data['_sub_realm'] = True
        data['name'] = 'ping1'
        data['_users_read'] = [self.user4_id]
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Get the commands for realm All
        params = {'where': json.dumps({'_realm': self.realmAll_id})}
        response = requests.get(self.endpoint + '/command', params=params, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 3

        data['_sub_realm'] = False
        data['name'] = 'ping2'
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Get the commands for realm All
        params = {'where': json.dumps({'_realm': self.realmAll_id})}
        response = requests.get(self.endpoint + '/command', params=params, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 4

        data['_realm'] = self.sluis
        data['_sub_realm'] = False
        data['name'] = 'ping3'
        data['_users_read'] = [self.user4_id]
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Get the commands for realm Sluis
        params = {'where': json.dumps({'_realm': self.sluis})}
        response = requests.get(self.endpoint + '/command', params=params, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1

        data['_realm'] = self.dagobah
        data['_sub_realm'] = False
        data['name'] = 'ping4'
        data['_users_read'] = [self.user4_id]
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Get the commands for realm Dagobah
        params = {'where': json.dumps({'_realm': self.dagobah})}
        response = requests.get(self.endpoint + '/command', params=params, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1

        data['_realm'] = self.hoth
        data['_sub_realm'] = False
        data['name'] = 'ping5'
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Get the commands for realm Hoth
        params = {'where': json.dumps({'_realm': self.hoth})}
        response = requests.get(self.endpoint + '/command', params=params, auth=self.auth)
        resp = response.json()
        assert len(resp['_items']) == 1

        # Now we have some commands in all the realms:
        # - All: 3 commands visible in sub-realms and 1 only for All realm
        # - Hoth: 1 not visible in sub-realms
        # - Sluis: 1 not visible in sub-realms
        # - Dagobah: 1 not visible in sub-realms

        params = {'username': 'user1', 'password': 'test', 'action': 'generate'}
        # get token user 1
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user1_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        params = {'username': 'user2', 'password': 'test', 'action': 'generate'}
        # get token user 2
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user2_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        params = {'username': 'user3', 'password': 'test', 'action': 'generate'}
        # get token user 3
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user3_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        params = {'username': 'user4', 'password': 'test', 'action': 'generate'}
        # get token user 4
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user4_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        params = {'username': 'user5', 'password': 'test', 'action': 'generate'}
        # get token user 5
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user5_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        # Get commands for each user
        # User 1 - read right on Sluis realm and sub-realms
        # Should see 3 commands from All realm, 1 from Sluis and 1 from Dagobah
        response = requests.get(self.endpoint + '/command', params={'sort': "name"},
                                auth=user1_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 5)
        self.assertEqual(resp['_meta']['total'], 5)

        # User 2 - read right on Hoth realm and sub-realms
        # Should see 3 commands from All realm, 1 from Hoth
        response = requests.get(self.endpoint + '/command', params={'sort': "name"},
                                auth=user2_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 4)
        self.assertEqual(resp['_meta']['total'], 4)

        # User 3 - read right on All realm and no sub-realms
        # Should see 4 commands from All realm
        response = requests.get(self.endpoint + '/command', params={'sort': "name"},
                                auth=user3_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 4)
        self.assertEqual(resp['_meta']['total'], 4)

        # User 4 - read right on Sluis realm and no sub-realms + custom right on command
        # Should see 3 commands from All realm, 1 from Sluis
        response = requests.get(self.endpoint + '/command', params={'sort': "name"},
                                auth=user4_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 4)
        self.assertEqual(resp['_meta']['total'], 4)

        # User 5 - read right on Sluis realm and no sub-realms
        # Should see 3 commands from All realm, 1 from Sluis
        response = requests.get(self.endpoint + '/command', params={'sort': "name"},
                                auth=user5_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 4)
        self.assertEqual(resp['_meta']['total'], 4)

    def test_restrict_right(self):
        """Test user with restriction in realms

        user6 has read rights on Sluis realm and its sub-realms. He will not get the All realm...

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        params = {'username': 'user6', 'password': 'test', 'action': 'generate'}
        # get token user 6
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        user6_auth = requests.auth.HTTPBasicAuth(resp['token'], '')

        # Check user6 with realms, must have 2 realms : Sluis and Dagobah
        response = requests.get(self.endpoint + '/realm', params={'sort': "name"},
                                auth=user6_auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_meta']['total'], 2)
        self.assertEqual('Dagobah', resp['_items'][0]['name'])
        self.assertEqual('Sluis', resp['_items'][1]['name'])

        # check _parent and _tree_parents of realms are in realms we have access
        parent = ''
        for realm in resp['_items']:
            if realm['name'] == 'Sluis':
                parent = realm['_id']
        for realm in resp['_items']:
            if realm['name'] == 'Sluis':
                assert realm['_parent'] is None
                assert realm['_tree_parents'] == []
            elif realm['name'] == 'Dagobah':
                assert realm['_parent'] == parent
                assert realm['_tree_parents'] == [parent]
