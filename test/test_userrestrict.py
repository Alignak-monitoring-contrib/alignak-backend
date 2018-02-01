#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the userrestrict (uipref)
"""

from __future__ import print_function

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestUserrestrict(unittest2.TestCase):
    """This class test the userrestrictrole (uipref)"""

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

        # get user admin
        response = requests.get(cls.endpoint + '/user', auth=cls.auth)
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

    def crud_command(self, my_auth, resource='command', name='test', crud='crud', extra_data=None):
        # pylint: disable=too-many-locals, too-many-arguments
        """Create, read, update and delete a command

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # data for objet creation
        data = {
            'name': name,
            '_realm': self.realmAll_id,
            '_sub_realm': True
        }

        if extra_data:
            for key in extra_data:
                if extra_data[key] == 'remove':
                    data.pop(key)
                else:
                    data.update({key: extra_data[key]})

        # - create with provided authentication
        print("Try to create a new %s" % resource)
        resp = requests.post(self.endpoint + '/' + resource, json=data,
                             headers=headers, auth=my_auth)
        resp = resp.json()
        print("Result: %s" % resp)
        if 'c' in crud:
            print("Created")
            assert resp['_status'] == 'OK'
        else:
            print("Refused: %s" % resp)
            assert resp == {
                u'_status': u'ERR',
                u'_error': {u'message': u'Not allowed to POST on this endpoint / resource.',
                            u'code': 401}}
            # Create with default super-admin authentication
            resp = requests.post(self.endpoint + '/' + resource, json=data, headers=headers,
                                 auth=self.auth)
            resp = resp.json()
            assert resp['_status'] == 'OK'

        # - check resource read
        print("Try to get %s" % resource)
        params = {}
        if 'name' in data:
            params = {'where': json.dumps({'name': name})}
        response = requests.get(self.endpoint + '/' + resource, params=params, auth=my_auth)
        resp = response.json()
        print("Result: %s" % resp)
        cmd_id = None
        cmd_etag = None
        if 'r' in crud:
            print("Got")
            self.assertEqual(len(resp['_items']), 1)
            if 'name' in data:
                self.assertEqual(resp['_items'][0]['name'], name)
            cmd_id = resp['_items'][0]['_id']
            cmd_etag = resp['_items'][0]['_etag']
        else:
            print("Refused: %s" % resp)
            assert resp == {
                u'_status': u'ERR',
                u'_error': {u'message': u'Not allowed to POST on this endpoint / resource.',
                            u'code': 401}}

        # - check resource update
        print("Try to update %s" % resource)
        headers = {'Content-Type': 'application/json', 'If-Match': cmd_etag}
        patch_data = {'alias': 'Updated alias'}
        resp = requests.patch(self.endpoint + '/' + resource + '/' + cmd_id, json=patch_data,
                              headers=headers, auth=my_auth)
        resp = resp.json()
        print("Result: %s" % resp)
        if 'u' in crud:
            print("Updated")
            if resp['_status'] == 'ERR':
                assert resp == {u'_status': u'ERR', u'_issues': {u'alias': u'unknown field'}}
            else:
                assert resp['_status'] == 'OK'

                # - read to get new etag and confirm update
                params = {'where': json.dumps({'name': name})}
                response = requests.get(self.endpoint + '/' + resource, params=params, auth=my_auth)
                resp = response.json()
                self.assertEqual(len(resp['_items']), 1)
                self.assertEqual(resp['_items'][0]['name'], name)
                self.assertEqual(resp['_items'][0]['alias'], "Updated alias")
        else:
            print("Refused: %s" % resp)
            assert resp == {
                u'_status': u'ERR',
                u'_error': {u'message': u'Not allowed to PATCH on this endpoint / resource.',
                            u'code': 401}}

        # - delete element
        print("Try to delete %s" % resource)
        params = {}
        if 'name' in data:
            params = {'where': json.dumps({'name': name})}
        response = requests.get(self.endpoint + '/' + resource, params=params, auth=my_auth)
        resp = response.json()
        print("Result: %s" % resp)
        if 'name' in data:
            self.assertEqual(len(resp['_items']), 1)
        cmd_id = resp['_items'][len(resp['_items']) - 1]['_id']
        cmd_etag = resp['_items'][len(resp['_items']) - 1]['_etag']

        headers = {'If-Match': cmd_etag}
        resp = requests.delete(self.endpoint + '/' + resource + '/' + cmd_id,
                               headers=headers, auth=my_auth)
        print("Result: %s" % resp)
        if 'd' in crud:
            print("Deleted")
            assert resp.status_code == 204

            # - read to confirm deletion
            params = {'where': json.dumps({'name': name})}
            response = requests.get(self.endpoint + '/' + resource, params=params, auth=my_auth)
            resp = response.json()
            self.assertEqual(len(resp['_items']), 0)
        else:
            print("Refused: %s" % resp)
            # Note that delete do not return the same pattern as update or post when 401 !
            assert resp.status_code == 401
            # It should be this:
            # assert resp == {
            #     u'_status': u'ERR',
            #     u'_error': {u'message': u'Not allowed to DELETE on this endpoint / resource.',
            #                 u'code': 401}}

    def test_user_rights_default_super_admin(self):
        """Test that the default super-admin has all the rights (CRUD)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Get default super_admin token
        params = {'username': 'admin', 'password': 'admin'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()

        my_auth = requests.auth.HTTPBasicAuth(resp['token'], '')
        self.crud_command(my_auth, 'realm', 'default-super-admin',
                          extra_data={'_realm': 'remove', '_sub_realm': 'remove'})
        self.crud_command(my_auth, 'command', 'default-super-admin')
        self.crud_command(my_auth, 'timeperiod', 'default-super-admin')
        self.crud_command(my_auth, 'host', 'default-super-admin')

        # Create an host resource
        data = {
            'name': 'my_host',
            '_realm': self.realmAll_id,
            '_sub_realm': True
        }
        resp = requests.post(self.endpoint + '/host', json=data,
                             headers=headers, auth=my_auth)
        resp = resp.json()
        host_id = resp['_id']

        self.crud_command(my_auth, 'service', 'default-super-admin',
                          extra_data={'host': host_id})
        self.crud_command(my_auth, 'user', 'default-super-admin')
        self.crud_command(my_auth, 'alignak', 'default-super-admin')
        self.crud_command(my_auth, 'alignakdaemon', 'default-super-admin',
                          extra_data={'alive': True, 'last_check': 123456789,
                                      'passive': False, 'reachable': True,
                                      'address': '127.0.0.1', 'spare': False,
                                      'type': 'arbiter', 'port': 7770})
        self.crud_command(my_auth, 'statsd', 'default-super-admin',
                          extra_data={'address': '127.0.0.1'})
        self.crud_command(my_auth, 'graphite', 'default-super-admin',
                          extra_data={'carbon_address': '127.0.0.1',
                                      'graphite_address': '127.0.0.1'})
        self.crud_command(my_auth, 'influxdb', 'default-super-admin',
                          extra_data={'database': 'db', 'address': '127.0.0.1',
                                      'login': 'login', 'password': 'password'})
        self.crud_command(my_auth, 'grafana', 'default-super-admin',
                          extra_data={'apikey': '123456789', 'address': '127.0.0.1'})
        self.crud_command(my_auth, 'history', 'default-super-admin',
                          extra_data={'type': 'webui.comment', 'name': 'remove'})
        # self.crud_command(my_auth, 'logcheckresult', 'default-super-admin')

        # Create a service resource
        data = {
            'host': resp['_id'],
            'name': 'my_service',
            '_realm': self.realmAll_id,
            '_sub_realm': True
        }
        resp = requests.post(self.endpoint + '/service', json=data,
                             headers=headers, auth=my_auth)
        resp = resp.json()
        service_id = resp['_id']
        self.crud_command(my_auth, 'actionacknowledge', 'default-super-admin',
                          extra_data={
                              'host': host_id, 'service': service_id,
                              'user': self.user_admin['_id'], 'name': 'remove'})
        self.crud_command(my_auth, 'actiondowntime', 'default-super-admin',
                          extra_data={
                              'host': host_id, 'service': service_id,
                              'user': self.user_admin['_id'], 'name': 'remove'})
        self.crud_command(my_auth, 'actionforcecheck', 'default-super-admin',
                          extra_data={
                              'host': host_id, 'service': service_id,
                              'user': self.user_admin['_id'], 'name': 'remove'})

    def test_user_rights_super_admin(self):
        """Test that a newly created super-admin has all the rights (CRUD)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a super_admin which is a super admin user
        data = {
            'name': 'super_admin', 'password': 'test', 'back_role_super_admin': True,
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()

        # Get new super_admin token
        params = {'username': 'super_admin', 'password': 'test'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()

        my_auth = requests.auth.HTTPBasicAuth(resp['token'], '')
        self.crud_command(my_auth, 'command', 'new-super-admin')

    def test_user_rights_normal_user_default_rights(self):
        """Test that a newly created user only has read-only rights

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a normal user (not a super-admin user)
        data = {
            'name': 'normal_user', 'password': 'test', 'back_role_super_admin': False,
            '_realm': self.realmAll_id
        }
        requests.post(self.endpoint + '/user', json=data, headers=headers, auth=self.auth)

        # Get new user token
        params = {'username': 'normal_user', 'password': 'test'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()

        my_auth = requests.auth.HTTPBasicAuth(resp['token'], '')
        print("auth: %s" % resp['token'])
        self.crud_command(my_auth, 'command', 'default-user', crud='r')

    def test_user_rights_normal_user_full_crud(self):
        """Test that a newly created user has all the rights (CRUD)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add a normal user (not a super-admin user)
        data = {
            'name': 'normal_user_full', 'password': 'test', 'back_role_super_admin': False,
            '_realm': self.realmAll_id
        }
        response = requests.post(self.endpoint + '/user', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        user_id = resp['_id']

        # Get new user restrict role
        params = {'where': json.dumps({'user': user_id})}
        response = requests.get(self.endpoint + '/userrestrictrole', params=params, auth=self.auth)
        resp = response.json()
        print("URR: %s" % resp)
        assert len(resp['_items']) == 1
        assert resp['_items'][0]['crud'] == ['read']
        assert resp['_items'][0]['resource'] == '*'

        # Update user's rights - set full CRUD rights
        headers = {'Content-Type': 'application/json', 'If-Match': resp['_items'][0]['_etag']}
        data = {'crud': ['create', 'read', 'update', 'delete', 'custom']}
        resp = requests.patch(self.endpoint + '/userrestrictrole/' + resp['_items'][0]['_id'],
                              json=data, headers=headers, auth=self.auth)
        resp = resp.json()
        assert resp['_status'] == 'OK'

        # Get new user restrict role
        params = {'where': json.dumps({'user': user_id})}
        response = requests.get(self.endpoint + '/userrestrictrole', params=params, auth=self.auth)
        resp = response.json()
        print("URR: %s" % resp)
        assert len(resp['_items']) == 1
        assert resp['_items'][0]['crud'] == ['create', 'read', 'update', 'delete', 'custom']
        assert resp['_items'][0]['resource'] == '*'

        # Get new user token
        params = {'username': 'normal_user_full', 'password': 'test'}
        response = requests.post(self.endpoint + '/login', json=params, headers=headers)
        resp = response.json()

        my_auth = requests.auth.HTTPBasicAuth(resp['token'], '')
        self.crud_command(my_auth, 'command', 'default-powered-user', crud='crud')
