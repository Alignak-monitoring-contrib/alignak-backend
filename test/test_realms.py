#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the realms and the tree feature of realms (children)
"""

from __future__ import print_function
import time
import shlex
import subprocess
import copy
import requests
import unittest2


class TestRealms(unittest2.TestCase):
    """
    This class test realms and tree feature
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

        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000',
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
        cls.realmAll_id = resp['_items'][0]['_id']

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
        Delete resources in backend

        :return: None
        """
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis', 'realm']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_add_realm(self):
        """
        Test add realms, add children, check than we can't delete a realm if it has children

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_name = {'sort': 'name'}
        sort_level = {'sort': '_level'}

        response = requests.get(self.endpoint + '/realm', params=sort_level, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(len(re), 1)

        # * Add sub_realms
        data = {"name": "All A", "_parent": self.realmAll_id}
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realmAll_A_id = copy.copy(resp['_id'])

        response = requests.get(self.endpoint + '/realm', params=sort_level, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(re[1]['name'], "All A")
        self.assertEqual(re[1]['_parent'], self.realmAll_id)
        self.assertEqual(re[1]['_level'], 1)
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [])
        # it's realm "All"
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id])

        data = {"name": "All B", "_parent": self.realmAll_id}
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realmAll_B_id = copy.copy(resp['_id'])

        response = requests.get(self.endpoint + '/realm', params=sort_level, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id])

        # ** Add sub_sub_realms
        data = {"name": "All A.1", "_parent": realmAll_A_id}
        requests.post(self.endpoint + '/realm', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/realm', params=sort_name, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(re[2]['name'], "All A.1")
        self.assertEqual(re[2]['_parent'], realmAll_A_id)
        self.assertEqual(re[2]['_level'], 2)
        self.assertEqual(re[2]['_tree_parents'], [self.realmAll_id, realmAll_A_id])
        self.assertEqual(re[2]['_tree_children'], [])
        realmAll_A1_id = copy.copy(re[2]['_id'])

        # ** Realm All A
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [realmAll_A1_id])

        # ** Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id])

        # *** Add sub_sub_sub_realms
        data = {"name": "All A.1.a", "_parent": realmAll_A1_id}
        requests.post(self.endpoint + '/realm', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/realm', params=sort_name, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(re[3]['name'], "All A.1.a")
        self.assertEqual(re[3]['_parent'], realmAll_A1_id)
        self.assertEqual(re[3]['_level'], 3)
        self.assertEqual(re[3]['_tree_parents'], [self.realmAll_id, realmAll_A_id, realmAll_A1_id])
        self.assertEqual(re[3]['_tree_children'], [])
        realmAll_A1a_id = copy.copy(re[3]['_id'])
        realmAll_A1a_etag = copy.copy(re[3]['_etag'])

        self.assertEqual(re[2]['name'], "All A.1")
        realmAll_A1_etag = copy.copy(re[2]['_etag'])

        # *** Realm All A
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [realmAll_A1_id, realmAll_A1a_id])

        # *** Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id,
                                                   realmAll_A1a_id])

        # Delete 'All A.1' will not work because have sub realm
        headers = {'If-Match': realmAll_A1_etag}
        response = requests.delete(self.endpoint + '/realm/' + realmAll_A1_id, headers=headers,
                                   auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_status'], "ERR")

        # Delete All A.1.a (can be deleted and remove ref to parents)
        headers = {'If-Match': realmAll_A1a_etag}
        response = requests.delete(self.endpoint + '/realm/' + realmAll_A1a_id, headers=headers,
                                   auth=self.auth)
        self.assertEqual(response.status_code, 204)

        response = requests.get(self.endpoint + '/realm', params=sort_level, auth=self.auth)
        resp = response.json()
        re = resp['_items']
        self.assertEqual(len(re), 4)
        # Realm All A.1
        self.assertEqual(re[3]['_tree_parents'], [self.realmAll_id, realmAll_A_id])
        self.assertEqual(re[3]['_tree_children'], [])

        # Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id])

        # verify we can't update _tree_parents of a realm manually
        response = requests.get(self.endpoint + '/realm', params={'where': '{"name":"All A.1"}'},
                                auth=self.auth)
        resp = response.json()
        re = resp['_items']
        data = {'_tree_parents': []}
        headers = {
            'Content-Type': 'application/json',
            'If-Match': re[0]['_etag']
        }
        response = requests.patch(self.endpoint + '/realm/' + realmAll_A1_id, json=data,
                                  headers=headers, auth=self.auth)
        self.assertEqual(response.status_code, 412)
        self.assertEqual(response.text, 'Update _tree_parents is forbidden')
