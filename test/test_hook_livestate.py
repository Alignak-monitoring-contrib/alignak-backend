#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test verify the different hooks used in the backend to fill livestates
"""

import json
import time
import shlex
import subprocess
import requests
import unittest2


class TestHookLivestate(unittest2.TestCase):
    """
    This class test the hooks used to fill livestates resource
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
        cls.realm_all = resp['_items'][0]['_id']

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
        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_add_host(self):
        """
        Test the livestate hook to create a livestate resource when create a new host

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")
        # Check if livestate right created
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['last_state'], 'UNREACHABLE')
        self.assertEqual(r[0]['last_state_type'], 'HARD')
        self.assertEqual(r[0]['last_check'], 0)
        self.assertEqual(r[0]['state_type'], 'HARD')
        self.assertEqual(r[0]['state'], 'UNREACHABLE')
        self.assertEqual(r[0]['host'], rh[0]['_id'])
        self.assertEqual(r[0]['service'], None)
        self.assertEqual(r[0]['business_impact'], 5)
        self.assertEqual(r[0]['type'], 'host')

    def test_add_service(self):
        """
        Test the livestate hook to create a livestate resource when create a new service

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh[0]['_id']
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)
        # Check if service right in backend
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['name'], "ping")

        # Check if livestate right created
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['last_state'], 'OK')
        self.assertEqual(r[1]['last_state_type'], 'HARD')
        self.assertEqual(r[1]['last_check'], 0)
        self.assertEqual(r[1]['state_type'], 'HARD')
        self.assertEqual(r[1]['state'], 'OK')
        self.assertEqual(r[1]['host'], rh[0]['_id'])
        self.assertEqual(r[1]['service'], rs[0]['_id'])
        self.assertEqual(r[1]['type'], 'service')

    def test_update_host_business_impact(self):
        """
        Test the livestate hook update the field business_impact in livestate resource when
        update the host

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        rh = response.json()

        data['name'] = 'srv002'
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)

        # Update business_impact
        datap = {'business_impact': 1}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        # check if business_impact of host changed
        params = {'sort': 'name'}
        response = requests.get(self.endpoint + '/host', params=params, auth=self.auth)
        resp = response.json()
        rh = resp['_items']

        self.assertEqual(rh[0]['business_impact'], 1)
        self.assertEqual(rh[1]['business_impact'], 5)

        # Check if livestate right updated
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]['business_impact'], 1)
        self.assertEqual(r[1]['business_impact'], 5)

    def test_update_service_business_impact(self):
        """
        Test the livestate hook update the field business_impact in livestate resource when
        update the service

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh[0]['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        response = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                 auth=self.auth)
        rs = response.json()

        # Update business_impact
        datap = {'business_impact': 1}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap, headers=headers_patch,
                       auth=self.auth)

        # check if business_impact of service changed
        response = requests.get(self.endpoint + '/service', params=sort_id, auth=self.auth)
        resp = response.json()
        rs = resp['_items']
        self.assertEqual(rs[0]['business_impact'], 1)

        # Check if livestate right updated
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']

        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['business_impact'], 1)

    def test_display_name_host__display_name(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_host in
        livestate resource when create and update the host (field display_name of host)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        for resource in ['host', 'livestate', 'livesynthesis']:
            requests.delete(self.endpoint + '/' + resource, auth=self.auth)

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['display_name'] = 'Server 001: srv001'
        data['alias'] = 'Server 001: srv001 alias'
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        responsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                  auth=self.auth)
        rh = responsep.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host host
        datap = {'name': 'srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 1)
        self.assertEqual(resp['_items'][0]['display_name_service'], '')
        self.assertEqual(resp['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__alias(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_host in
        livestate resource when create and update the host (field alias of host)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        data['alias'] = 'Server 001: srv001 alias'
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        reponsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        rh = reponsep.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001 alias')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host host
        datap = {'name': 'srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 1)
        self.assertEqual(resp['_items'][0]['display_name_service'], '')
        self.assertEqual(resp['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_host__host(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_host in
        livestate resource when create and update the host (field name of host)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        reponsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        rh = reponsep.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001')

        # * Case we update host host
        datap = {'name': 'srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001-1')

        # * Case we update host alias
        datap = {'alias': 'srv001 alias beta'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        responseph = requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rh = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[0]['display_name_host'], 'srv001 alias beta')

        # * Case we update host display_name
        datap = {'display_name': 'Server 001: srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 1)
        self.assertEqual(resp['_items'][0]['display_name_service'], '')
        self.assertEqual(resp['_items'][0]['display_name_host'], 'Server 001: srv001-1')

    def test_display_name_service__display_name(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_service in
        livestate resource when create and update the service (field display_name of service)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_items'][0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = resp['_items'][0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        reponsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        rh = reponsep.json()

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh['_id']
        data['check_command'] = resp['_items'][0]['_id']
        data['display_name'] = 'ping check of server srv001'
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'], 'ping check of server srv001')

        for resource in ['host', 'service', 'command', 'livestate', 'livesynthesis']:
            requests.delete(self.endpoint + '/' + resource, auth=self.auth)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_items'][0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = resp['_items'][0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        responsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                  auth=self.auth)
        rh = responsep.json()

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh['_id']
        data['check_command'] = resp['_items'][0]['_id']
        data['display_name'] = 'ping check of server srv001'
        data['alias'] = 'check ping'
        data['_realm'] = self.realm_all
        responses = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                  auth=self.auth)
        rs = responses.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service alias
        datap = {'alias': 'check ping'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseph = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service service
        datap = {'name': 'check_ping'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseph = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseph.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'], 'ping check of server srv001')

        # * Case we update service display_name
        datap = {'display_name': 'ping check of server srv001 (2)'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'],
                         'ping check of server srv001 (2)')

    def test_display_name_service__alias(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_service in
        livestate resource when create and update the service (field alias of service)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        responsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                  auth=self.auth)
        rh = responsep.json()

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['alias'] = 'ping check alias'
        data['_realm'] = self.realm_all
        responses = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                  auth=self.auth)
        rs = responses.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias')

        # * Case we update service alias
        datap = {'alias': 'ping check alias (2)'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseps = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseps.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service service
        datap = {'name': 'check-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseps = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseps.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping check alias (2)')

        # * Case we update service display_name
        datap = {'display_name': 'check ping for srv001'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 2)
        self.assertEqual(resp['_items'][1]['display_name_host'], 'srv001')
        self.assertEqual(resp['_items'][1]['display_name_service'], 'check ping for srv001')

    def test_display_name_service__service(self):
        """
        Test the livestate hook fill (on creation and update) the field display_name_service in
        livestate resource when create and update the service (field name of service)

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        responsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                  auth=self.auth)
        rh = responsep.json()

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        responses = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                  auth=self.auth)
        rs = responses.json()

        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping')

        # * Case we update service service
        datap = {'name': 'ping-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseps = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseps.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping-1')

        # * Case we update service alias
        datap = {'alias': 'ping alias'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        responseps = requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                                    headers=headers_patch, auth=self.auth)
        rs = responseps.json()
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'ping alias')

        # * Case we update service display_name
        datap = {'display_name': 'check ping srv001'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rs['_etag']
        }
        requests.patch(self.endpoint + '/service/' + rs['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[1]['display_name_host'], 'srv001')
        self.assertEqual(r[1]['display_name_service'], 'check ping srv001')

    def test_update_display_name_host_and_check_service(self):
        """
        Test if update display_name of host is updated on livestate related with host and all
        services linked with this host

        :return:
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        rc = resp['_items']
        self.assertEqual(rc[0]['name'], "ping")

        # add host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        responsep = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                  auth=self.auth)
        rh = responsep.json()

        # Add service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = rh['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

        datap = {'display_name': 'Server 001: srv001-1'}
        headers_patch = {
            'Content-Type': 'application/json',
            'If-Match': rh['_etag']
        }
        requests.patch(self.endpoint + '/host/' + rh['_id'], json=datap,
                       headers=headers_patch, auth=self.auth)
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        r = resp['_items']
        self.assertEqual(len(r), 2)
        self.assertEqual(r[0]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r[0]['display_name_service'], '')
        self.assertEqual(r[1]['display_name_host'], 'Server 001: srv001-1')
        self.assertEqual(r[1]['display_name_service'], 'ping')

    def test_host_template(self):
        """
        Test livestate resource not created when create a host template

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        sort_id = {'sort': '_id'}
        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        requests.post(self.endpoint + '/command', json=data, headers=headers, auth=self.auth)
        # Check if command right in backend
        response = requests.get(self.endpoint + '/command', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_items'][0]['name'], "ping")

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = resp['_items'][0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        data['_is_template'] = True
        requests.post(self.endpoint + '/host', json=data, headers=headers, auth=self.auth)
        # Check if host right in backend
        response = requests.get(self.endpoint + '/host', params=sort_id, auth=self.auth)
        resp = response.json()
        rh = resp['_items']
        self.assertEqual(rh[0]['name'], "srv001")
        self.assertEqual(rh[0]['_is_template'], True)
        # Check if livestate right created
        response = requests.get(self.endpoint + '/livestate', params=sort_id, auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 0)
