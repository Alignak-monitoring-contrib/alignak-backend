#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check the sending of Alignak notifications when some items are created/deleted
"""

import os
import json
import time
import shlex
import subprocess
import requests
import unittest2
from alignak_backend.models.host import get_schema as host_schema
from alignak_backend.models.user import get_schema as user_schema


class TestAlignakNotification(unittest2.TestCase):
    """
    This class test the hooks used for hosts and services templates
    """

    maxDiff = None

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
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'abtn'
        os.environ['ALIGNAK_BACKEND_CONFIGURATION_FILE'] = './cfg/settings/settings_cron.json'

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

        # Login as admin
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin', 'action': 'generate'}
        response = requests.post(cls.endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth = requests.auth.HTTPBasicAuth(cls.token, '')

        # Get user admin
        response = requests.get(cls.endpoint + '/user', auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]

        # Get default realm
        response = requests.get(cls.endpoint + '/realm', auth=cls.auth,
                                params={'where': json.dumps({'name': 'All'})})
        resp = response.json()
        cls.realm_all = resp['_items'][0]['_id']

        # Get default host
        response = requests.get(cls.endpoint + '/host', auth=cls.auth,
                                params={'where': json.dumps({'name': '_dummy'})})
        resp = response.json()
        cls.default_host = resp['_items'][0]['_id']

        # Get default host check_command
        response = requests.get(cls.endpoint + '/command', auth=cls.auth,
                                params={'where': json.dumps({'name': '_internal_host_up'})})
        resp = response.json()
        cls.default_host_check_command = resp['_items'][0]['_id']

        # Get default service check_command
        response = requests.get(cls.endpoint + '/command', auth=cls.auth,
                                params={'where': json.dumps({'name': '_echo'})})
        resp = response.json()
        cls.default_service_check_command = resp['_items'][0]['_id']

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
        Delete resources after each test

        :return: None
        """
        for resource in ['host', 'service', 'command', 'livesynthesis']:
            response = requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)
            assert response.status_code == 204

    @unittest2.skip("Runs locally but not in Travis build... :/")
    def test_host_creation_notifications(self):
        """Create a new host with default check command and realm - raises an Alignak notification

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Clear the alignak notifications
        from alignak_backend.app import app
        with app.test_request_context():
            alignak_notifications_db = app.data.driver.db['alignak_notifications']
            alignak_notifications_db.drop()

        # Create an host without template
        data = {'name': 'host_1'}
        resp = requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        resp = resp.json()
        assert '_id' in resp
        assert '_created' in resp
        assert '_updated' in resp
        # host was created with only a name information...

        # Get the newly created host
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        host = response.json()
        self.assertEqual(host['name'], "host_1")
        self.assertEqual(host['_realm'], self.realm_all)
        self.assertEqual(host['check_command'], self.default_host_check_command)

        # Get the alignak notifications
        with app.test_request_context():
            alignak_notifications_db = app.data.driver.db['alignak_notifications']
            notifications = alignak_notifications_db.find()

            self.assertEqual(notifications.count(), 1)
            self.assertEqual(notifications[0]['event'], u'creation')
            self.assertEqual(notifications[0]['parameters'], u'host:host_1')
            self.assertEqual(notifications[0]['notification'], u'reload_configuration')

        # Add a check command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)

        # Check command exists in the backend
        response = requests.get(self.endpoint + '/command', auth=self.auth,
                                params={'where': json.dumps({'name': 'ping'})})
        resp = response.json()
        cmd = resp['_items'][0]
        self.assertEqual(cmd['name'], "ping")

        # Create an host template
        data = {
            'name': 'tpl_1',
            'check_command': cmd['_id'],
            '_is_template': True
        }
        resp = requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        resp = resp.json()
        assert '_id' in resp
        assert '_created' in resp
        assert '_updated' in resp

        # Get the newly created host
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        tpl = response.json()
        self.assertEqual(tpl['name'], "tpl_1")
        self.assertEqual(tpl['_realm'], self.realm_all)
        self.assertEqual(tpl['check_command'], cmd['_id'])

        # Get the alignak notifications
        with app.test_request_context():
            alignak_notifications_db = app.data.driver.db['alignak_notifications']
            notifications = alignak_notifications_db.find()

            self.assertEqual(notifications.count(), 2)
            self.assertEqual(notifications[0]['event'], u'creation')
            self.assertEqual(notifications[0]['parameters'], u'host:host_1')
            self.assertEqual(notifications[0]['notification'], u'reload_configuration')
            self.assertEqual(notifications[1]['event'], u'creation')
            self.assertEqual(notifications[1]['parameters'], u'host:tpl_1')
            self.assertEqual(notifications[1]['notification'], u'reload_configuration')

        # Create an host inheriting from the new template
        data = {
            'name': 'host_2',
            '_templates': [tpl['_id']]
        }
        resp = requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        resp = resp.json()
        assert '_id' in resp
        assert '_created' in resp
        assert '_updated' in resp

        # Get the newly created host
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        host = response.json()
        self.assertEqual(host['name'], "host_2")
        self.assertEqual(host['_realm'], self.realm_all)
        self.assertEqual(host['_templates'], [tpl['_id']])
        self.assertEqual(host['check_command'], cmd['_id'])

        # Get the alignak notifications
        with app.test_request_context():
            alignak_notifications_db = app.data.driver.db['alignak_notifications']
            notifications = alignak_notifications_db.find()

            self.assertEqual(notifications.count(), 3)
            self.assertEqual(notifications[0]['event'], u'creation')
            self.assertEqual(notifications[0]['parameters'], u'host:host_1')
            self.assertEqual(notifications[0]['notification'], u'reload_configuration')
            self.assertEqual(notifications[1]['event'], u'creation')
            self.assertEqual(notifications[1]['parameters'], u'host:tpl_1')
            self.assertEqual(notifications[1]['notification'], u'reload_configuration')
            self.assertEqual(notifications[2]['event'], u'creation')
            self.assertEqual(notifications[2]['parameters'], u'host:host_2')
            self.assertEqual(notifications[2]['notification'], u'reload_configuration')

        from alignak_backend.app import cron_alignak
        cron_alignak()
