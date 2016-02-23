#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import time
import subprocess
import json
from alignak_backend_client.client import Backend, BackendException


class TestRealms(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = subprocess.Popen(['uwsgi', '-w', 'alignakbackend:app', '--socket', '0.0.0.0:5000', '--protocol=http', '--enable-threads'])
        time.sleep(3)
        cls.backend = Backend('http://127.0.0.1:5000')
        cls.backend.login("admin", "admin", "force")
        cls.backend.delete("host", {})
        cls.backend.delete("command", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})
        contacts = cls.backend.get_all('contact')
        headers_contact = {'Content-Type': 'application/json'}
        for cont in contacts:
            if cont['name'] != 'admin':
                headers_contact['If-Match'] = cont['_etag']
                cls.backend.delete('contact/' + cont['_id'], headers_contact)

        realms = cls.backend.get_all('realm')
        headers_realm = {'Content-Type': 'application/json'}
        for cont in realms:
            if cont['name'] != 'All' and cont['_level'] != 0:
                headers_realm['If-Match'] = cont['_etag']
                cls.backend.delete('realm/' + cont['_id'], headers_realm)
            else :
                cls.realmAll_id = cont['_id']

    @classmethod
    def tearDownClass(cls):
        cls.backend.delete("contact", {})
        cls.p.kill()

    @classmethod
    def tearDown(cls):
        cls.backend.delete("host", {})
        cls.backend.delete("service", {})
        cls.backend.delete("command", {})
        cls.backend.delete("livestate", {})
        cls.backend.delete("livesynthesis", {})
        cls.backend.delete("realm", {})

    def test_add_realm(self):
        # * Add sub_realms
        data = {"name": "All A", "_parent": self.realmAll_id}
        resp = self.backend.post("realm", data)
        realmAll_A_id = resp['_id']

        re = self.backend.get_all('realm', {'sort': "_level"})
        self.assertEqual(re[1]['name'], "All A")
        self.assertEqual(re[1]['_parent'], self.realmAll_id)
        self.assertEqual(re[1]['_level'], 1)
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [])
        # it's realm "All"
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id])

        data = {"name": "All B", "_parent": self.realmAll_id}
        resp = self.backend.post("realm", data)
        realmAll_B_id = resp['_id']

        re = self.backend.get_all('realm', {'sort': "_level"})
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id])

        # ** Add sub_sub_realms
        data = {"name": "All A.1", "_parent": realmAll_A_id}
        self.backend.post("realm", data)

        re = self.backend.get_all('realm', {'sort': "_level"})
        self.assertEqual(re[3]['name'], "All A.1")
        self.assertEqual(re[3]['_parent'], realmAll_A_id)
        self.assertEqual(re[3]['_level'], 2)
        self.assertEqual(re[3]['_tree_parents'], [self.realmAll_id, realmAll_A_id])
        self.assertEqual(re[3]['_tree_children'], [])
        realmAll_A1_id = re[3]['_id']

        # ** Realm All A
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [realmAll_A1_id])

        # ** Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id])

        # *** Add sub_sub_sub_realms
        data = {"name": "All A.1.a", "_parent": realmAll_A1_id}
        self.backend.post("realm", data)

        re = self.backend.get_all('realm', {'sort': "_level"})
        self.assertEqual(re[4]['name'], "All A.1.a")
        self.assertEqual(re[4]['_parent'], realmAll_A1_id)
        self.assertEqual(re[4]['_level'], 3)
        self.assertEqual(re[4]['_tree_parents'], [self.realmAll_id, realmAll_A_id, realmAll_A1_id])
        self.assertEqual(re[4]['_tree_children'], [])
        realmAll_A1a_id = re[4]['_id']
        realmAll_A1a_etag = re[4]['_etag']

        self.assertEqual(re[3]['name'], "All A.1")
        realmAll_A1_etag = re[3]['_etag']

        # *** Realm All A
        self.assertEqual(re[1]['_tree_parents'], [self.realmAll_id])
        self.assertEqual(re[1]['_tree_children'], [realmAll_A1_id, realmAll_A1a_id])

        # *** Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id, realmAll_A1a_id])


        # Delete 'All A.1' will not work because have sub realm
        headers = {'If-Match': realmAll_A1_etag}
        with self.assertRaisesRegexp(BackendException, '409 Client Error: CONFLICT'):
            self.backend.delete('/'.join(['realm', realmAll_A1_id]), headers)

        # Delete All A.1.a (can be deleted and remove ref to parents)
        headers = {'If-Match': realmAll_A1a_etag}
        resp = self.backend.delete('/'.join(['realm', realmAll_A1a_id]), headers)
        self.assertEqual(resp, {})

        re = self.backend.get_all('realm', {'sort': "_level"})
        # Realm All A.1
        self.assertEqual(re[3]['_tree_parents'], [self.realmAll_id, realmAll_A_id])
        self.assertEqual(re[3]['_tree_children'], [])

        # Realm All
        self.assertEqual(re[0]['_tree_parents'], [])
        self.assertEqual(re[0]['_tree_children'], [realmAll_A_id, realmAll_B_id, realmAll_A1_id])

        # verify we can't update _tree_parents of a realm manually
        re = self.backend.get_all('realm', {'where': '{"name":"All A.1"}'})
        headers = {
            'Content-Type': 'application/json',
            'If-Match': re[0]['_etag']
        }
        data = {'_tree_parents': []}
        with self.assertRaisesRegexp(BackendException, 'error code 412: Update _tree_parents is forbid'):
            self.backend.patch('realm/%s' % realmAll_A1_id,
                               data, headers)
