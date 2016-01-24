#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest2
import time
import subprocess
import json
from alignak_backend_client.client import Backend


class TestRights(unittest2.TestCase):

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
            if cont['name'] != 'All':
                headers_realm['If-Match'] = cont['_etag']
                cls.backend.delete('realm/' + cont['_id'], headers_realm)
            else :
                cls.realmAll_id = cont['_id']

        # Add realm
        data = {'name': 'Hoth', "_parent": cls.realmAll_id}
        resp = cls.backend.post("realm", data)
        cls.hoth = resp['_id']

        data = {'name': 'Sluis', "_parent": cls.realmAll_id}
        resp = cls.backend.post("realm", data)
        cls.sluis = resp['_id']

        data = {'name': 'Dagobah', "_parent": cls.sluis}
        resp = cls.backend.post("realm", data)
        cls.dagobah = resp['_id']

        # Add contacts / users
        data = {'name': 'user1', 'password': 'test', 'back_role_super_admin': False}
        resp = cls.backend.post('contact', data)
        cls.user1_id = resp['_id']
        data = {'contact': resp['_id'], 'realm': cls.sluis, 'resource': 'command', 'crud': 'read',
                'sub_realm': True}
        cls.backend.post('contactrestrictrole', data)

        data = {'name': 'user2', 'password': 'test', 'back_role_super_admin': False}
        resp = cls.backend.post('contact', data)
        cls.user2_id = resp['_id']
        data = {'contact': resp['_id'], 'realm': cls.hoth, 'resource': 'command', 'crud': 'read'}
        cls.backend.post('contactrestrictrole', data)

        data = {'name': 'user3', 'password': 'test', 'back_role_super_admin': False}
        resp = cls.backend.post('contact', data)
        cls.user3_id = resp['_id']

        data = {'name': 'user4', 'password': 'test', 'back_role_super_admin': False}
        resp = cls.backend.post('contact', data)
        cls.user4_id = resp['_id']
        data = {'contact': resp['_id'], 'realm': cls.sluis, 'resource': 'command', 'crud': 'custom'}
        cls.backend.post('contactrestrictrole', data)


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

    def test_roles(self):
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_users_read'] = [self.user1_id]
        data['_realm'] = self.realmAll_id
        data['_sub_realm'] = True
        data['name'] = 'ping1'
        data['_users_read'] = [self.user4_id]
        self.backend.post("command", data)
        # Check if command right in backend
        rc = self.backend.get('command')
        self.assertEqual(rc['_items'][0]['name'], "ping1")

        data['_sub_realm'] = False
        data['name'] = 'ping2'
        self.backend.post("command", data)

        data['_realm'] = self.sluis
        data['_sub_realm'] = False
        data['name'] = 'ping3'
        data['_users_read'] = [self.user4_id]
        self.backend.post("command", data)

        data['_realm'] = self.dagobah
        data['_sub_realm'] = False
        data['name'] = 'ping4'
        data['_users_read'] = [self.user4_id]
        self.backend.post("command", data)

        data['_realm'] = self.hoth
        data['_sub_realm'] = False
        data['name'] = 'ping5'
        self.backend.post("command", data)


        #data = json.loads(open('cfg/host_srv001.json').read())
        #data['check_command'] = rc['_items'][0]['_id']
        #data['realm'] = self.naboo
        #self.backend.post("host", data)

        backend_user1 = Backend('http://127.0.0.1:5000')
        backend_user1.login("user1", "test", "force")

        backend_user2 = Backend('http://127.0.0.1:5000')
        backend_user2.login("user2", "test", "force")

        backend_user3 = Backend('http://127.0.0.1:5000')
        backend_user3.login("user3", "test", "force")

        backend_user4 = Backend('http://127.0.0.1:5000')
        backend_user4.login("user4", "test", "force")

        h = backend_user1.get_all('command', {'sort': "name"})
        self.assertEqual(len(h), 3)

        h = backend_user2.get_all('command', {'sort': "name"})
        self.assertEqual(len(h), 2)

        h = backend_user3.get_all('command', {'sort': "name"})
        self.assertEqual(len(h), 0)

        h = backend_user4.get_all('command', {'sort': "name"})
        self.assertEqual(len(h), 1)
