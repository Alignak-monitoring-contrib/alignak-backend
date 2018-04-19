#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check grafana and create dashboard + graphs
"""

from __future__ import print_function
import os
import json
from datetime import datetime, timedelta
import time
import shlex
from random import randint
import subprocess
import requests
import requests_mock
import unittest2
from bson.objectid import ObjectId
from alignak_backend.grafana import Grafana


class TestGrafana(unittest2.TestCase):
    """
    This class test grafana dashboard and panels
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
                                  '/tmp/uwsgi.pid', '--logto=/tmp/alignak_backend_grafana.log'])
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

        data = {"name": "All A", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_A = resp['_id']

        data = {"name": "All A1", "_parent": cls.realmAll_A}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_A1 = resp['_id']

        data = {"name": "All B", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realmAll_B = resp['_id']

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
        os.unlink("/tmp/alignak_backend_grafana.log")

    @classmethod
    def setUp(cls):
        """
        Create resources in the backend

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = cls.realm_all
        requests.post(cls.endpoint + '/command', json=data, headers=headers, auth=cls.auth)
        response = requests.get(cls.endpoint + '/command', auth=cls.auth)
        resp = response.json()
        rc = resp['_items']

        # Add an host
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = cls.realm_all
        data['ls_last_check'] = int(time.time())
        data['ls_perf_data'] = "rta=14.581000ms;1000.000000;3000.000000;0.000000 pl=0%;100;100;0"
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        resp = response.json()
        response = requests.get(cls.endpoint + '/host/' + resp['_id'], auth=cls.auth)
        cls.host_srv001 = response.json()

        # Add a service
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = cls.host_srv001['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = cls.realm_all
        data['name'] = 'load'
        data['ls_last_check'] = int(time.time())
        data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                               "load15=0.340;5.000;20.000;0;"
        response = requests.post(cls.endpoint + '/service', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.host_srv001_srv = resp['_id']

        # Add an host in realm A1
        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = cls.realmAll_A1
        data['name'] = "srv002"
        data['alias'] = "Server #2"
        data['tags'] = ["t2"]
        data['ls_last_check'] = int(time.time())
        data['ls_perf_data'] = "rta=14.581000ms;1000.000000;3000.000000;0.000000 pl=0%;100;100;0"
        response = requests.post(cls.endpoint + '/host', json=data, headers=headers, auth=cls.auth)
        resp = response.json()
        response = requests.get(cls.endpoint + '/host/' + resp['_id'], auth=cls.auth)
        cls.host_srv002 = response.json()

        # Add a service for srv002
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = cls.host_srv002['_id']
        data['check_command'] = rc[0]['_id']
        data['_realm'] = cls.realmAll_A1
        data['name'] = 'load'
        data['ls_last_check'] = int(time.time())
        data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                               "load15=0.340;5.000;20.000;0;"
        response = requests.post(cls.endpoint + '/service', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        response = requests.get(cls.endpoint + '/service/' + resp['_id'], auth=cls.auth)
        cls.host_srv002_srv = response.json()

    @classmethod
    def tearDown(cls):
        """
        Delete resources in backend

        :return: None
        """
        for resource in ['host', 'service', 'command', 'history',
                         'actionacknowledge', 'actiondowntime', 'actionforcecheck', 'grafana',
                         'graphite', 'influxdb', 'statsd']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_grafana_on_realms(self):
        """We can have more than 1 grafana server on each realm

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        # add a grafana on realm A + subrealm
        data = {
            'name': 'grafana All A+',
            'address': '192.168.0.100',
            'apikey': 'xxxxxxxxxxxx0',
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # add a grafana on realm All
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        grafana_all = resp['_id']

        # update the grafana on realm All + subrealm
        data = {'_sub_realm': True}
        headers_up = {
            'Content-Type': 'application/json',
            'If-Match': resp['_etag']
        }
        response = requests.patch(self.endpoint + '/grafana/' + grafana_all, json=data,
                                  headers=headers_up, auth=self.auth)
        self.assertEqual('OK', resp['_status'], resp)
        resp = response.json()

        # delete grafana on realm All
        headers_delete = {
            'Content-Type': 'application/json',
            'If-Match': resp['_etag']
        }
        response = requests.delete(self.endpoint + '/grafana/' + resp['_id'],
                                   headers=headers_delete, auth=self.auth)
        self.assertEqual(response.status_code, 204)

        response = requests.get(self.endpoint + '/grafana', auth=self.auth)
        resp = response.json()
        self.assertEqual(len(resp['_items']), 1)

        # add grafana on realm All + subrealm
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

    def test_2_graphites_same_realm(self):
        """Test 2 graphite on same realm, but only one can be affected to grafana on same realm

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        # Add grafana All + subrealms
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        grafana_all = resp['_id']

        # Add graphite_A in realm A associate to grafana
        data = {
            'name': 'graphite A sub',
            'carbon_address': '192.168.0.102',
            'graphite_address': '192.168.0.102',
            'prefix': 'my_A_sub',
            'grafana': grafana_all,
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Add graphite_B in realm A associate to grafana, so graphite_A not linked
        data = {
            'name': 'graphite B',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'my_B',
            'grafana': grafana_all,
            '_realm': self.realmAll_A
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        assert response.status_code == 412

        # todo try add in realm A1
        data = {
            'name': 'graphite B',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'my_B',
            'grafana': grafana_all,
            '_realm': self.realmAll_A1
        }
        requests.post(self.endpoint + '/graphite', json=data, headers=headers, auth=self.auth)

    def test_create_dashboard_panels_graphite(self):
        """Create dashboard into grafana with datasource graphite

        realms prefix is included

        :return: None
        """
        self._create_dashboard_panels_graphite(True)

    def test_create_dashboard_panels_graphite_no_realms_prefix(self):
        """Create dashboard into grafana with datasource graphite

        realms prefix is not included

        :return: None
        """
        self._create_dashboard_panels_graphite(False)

    def _create_dashboard_panels_graphite(self, realms_prefix):
        # pylint: disable=too-many-locals, too-many-nested-blocks
        """
        Create dashboard into grafana with datasource graphite

        realms_prefix is True or False to include the realms hierarchy
        in the Grafana panels targets

        :return: None
        """

        headers = {'Content-Type': 'application/json'}
        # Create grafana in realm All + subrealm
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        print("Grafana All: %s" % resp)
        grafana_all = resp['_id']

        # Create statsd in realm All + subrealm
        data = {
            'name': 'statsd All',
            'address': '192.168.0.101',
            'port': 8125,
            'prefix': 'alignak-statsd',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/statsd', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        statsd_all = resp['_id']

        # Create a graphite in All B linked to grafana with or without a realms prefix
        data = {
            'name': 'graphite B',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'my_B',
            'realms_prefix': realms_prefix,
            'grafana': grafana_all,
            'statsd': statsd_all,
            '_realm': self.realmAll_B
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Create a graphite in All A + subrealm linked to grafana
        data = {
            'name': 'graphite A sub',
            'carbon_address': '192.168.0.102',
            'graphite_address': '192.168.0.102',
            'prefix': 'my_A_sub',
            'realms_prefix': realms_prefix,
            'grafana': grafana_all,
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # test grafana class and code to create dashboard in grafana
        from alignak_backend.app import app, current_app
        with app.test_request_context():
            grafana_db = current_app.data.driver.db['grafana']
            grafanas = grafana_db.find()
            for grafana in grafanas:
                with requests_mock.mock() as mockreq:
                    ret = [{"id": 1, "orgId": 1, "name": 'alignak-graphite-graphite B',
                            "type": "grafana-simple-json-datasource",
                            "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/img/"
                                           "simpleJson_logo.svg",
                            "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                            "password": "", "user": "", "database": "", "basicAuth": True,
                            "basicAuthUser": "", "basicAuthPassword": "", "withCredentials": False,
                            "isDefault": False}]
                    mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                    mockreq.post('http://192.168.0.101:3000/api/datasources',
                                 json={'id': randint(2, 10)})
                    graf = Grafana(grafana)
                    assert len(graf.datasources) == 2
                    assert len(graf.timeseries) == 3
                    assert sorted([ObjectId(self.realmAll_B), ObjectId(self.realmAll_A),
                                   ObjectId(self.realmAll_A1)]) == sorted(graf.timeseries.keys())
                    for ts in graf.timeseries:
                        assert isinstance(ts, ObjectId)
                        assert graf.timeseries[ts]
                        print("TS: %s - %s - %s - %s" % (ts,
                                                         graf.timeseries[ts]['_realm'],
                                                         graf.timeseries[ts]['name'],
                                                         graf.timeseries[ts]['_id']))

                    assert graf.timeseries[ObjectId(self.realmAll_A)]['name'] == 'graphite A sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['name'] == 'graphite A sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['ts_prefix'] == \
                        'my_A_sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['statsd_prefix'] == ''
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['type'] == 'graphite'

                    assert graf.timeseries[ObjectId(self.realmAll_B)]['name'] == 'graphite B'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['ts_prefix'] == 'my_B'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['statsd_prefix'] == \
                        'alignak-statsd'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['type'] == 'graphite'
                history = mockreq.request_history
                methods = {'POST': 0, 'GET': 0}
                for h in history:
                    methods[h.method] += 1
                # One datasources created because we simulated that on still exists
                assert {'POST': 1, 'GET': 1} == methods

                # Create a dashboard for an host!
                with app.test_request_context():
                    with requests_mock.mock() as mockreq:
                        ret = [{"id": 1, "orgId": 1, "name": 'alignak-graphite-graphite B',
                                "type": "grafana-simple-json-datasource",
                                "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/"
                                               "img/simpleJson_logo.svg",
                                "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                                "password": "", "user": "", "database": "", "basicAuth": True,
                                "basicAuthUser": "", "basicAuthPassword": "",
                                "withCredentials": False, "isDefault": True},
                               {"id": 2, "orgId": 1, "name": 'alignak-graphite-graphite A sub',
                                "type": "grafana-simple-json-datasource",
                                "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/"
                                               "img/simpleJson_logo.svg",
                                "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                                "password": "", "user": "", "database": "", "basicAuth": True,
                                "basicAuthUser": "", "basicAuthPassword": "",
                                "withCredentials": False, "isDefault": False}]
                        mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                        mockreq.post('http://192.168.0.101:3000/api/datasources',
                                     json={'id': randint(2, 10)})
                        mockreq.post('http://192.168.0.101:3000/api/datasources/db', json='true')
                        mockreq.post('http://192.168.0.101:3000/api/dashboards/db', json='true')
                        graf = Grafana(grafana)
                        for ts in graf.timeseries:
                            print("TS: %s - %s - %s - %s" % (ts,
                                                             graf.timeseries[ts]['_realm'],
                                                             graf.timeseries[ts]['name'],
                                                             graf.timeseries[ts]['_id']))
                        # The host is not in a managed realm
                        assert self.host_srv001['_realm'] == self.realm_all
                        # Must convert to ObjectId because we are not really in Eve :)
                        self.host_srv001['_realm'] = ObjectId(self.host_srv001['_realm'])
                        assert self.host_srv001['_realm'] not in graf.timeseries.keys()
                        assert not graf.create_dashboard(self.host_srv001)

                        assert self.host_srv002['_realm'] == self.realmAll_A1
                        # Must convert to ObjectId because we are not really in Eve :)
                        self.host_srv002['_realm'] = ObjectId(self.host_srv002['_realm'])
                        assert ObjectId(self.host_srv002['_realm']) in graf.timeseries.keys()
                        assert graf.create_dashboard(self.host_srv002)
                        history = mockreq.request_history
                        methods = {'POST': 0, 'GET': 0}
                        for h in history:
                            methods[h.method] += 1
                            if h.method == 'POST':
                                dash = h.json()
                                # print("Post response: %s" % dash)
                                for row in dash['dashboard']['rows']:
                                    for panel in row['panels']:
                                        for target in panel['targets']:
                                            print("Target: %s" % target['target'])
                                            if not realms_prefix:
                                                assert '$ts_prefix.srv002' in target['target']
                                            else:
                                                assert '$ts_prefix.All' in target['target']
                                # assert len(dash['dashboard']['rows']) == 2
                        assert {'POST': 1, 'GET': 1} == methods

                    # check host and the service are tagged grafana and have the id
                    host_db = current_app.data.driver.db['host']
                    host002 = host_db.find_one({'_id': ObjectId(self.host_srv002['_id'])})
                    assert host002['ls_grafana']
                    assert host002['ls_grafana_panelid'] == 1
                    service_db = current_app.data.driver.db['service']
                    srv002 = service_db.find_one({'_id': ObjectId(self.host_srv002_srv['_id'])})
                    print("Service: %s" % srv002)
                    assert srv002['ls_grafana']
                    assert srv002['ls_grafana_panelid'] == 2

    def test_create_dashboard_panels_influxdb(self):
        # pylint: disable=too-many-locals
        """
        Create dashboard into grafana with datasource influxdb

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        # Create grafana in realm All + subrealm
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        print("Grafana All: %s" % resp)
        grafana_all = resp['_id']

        # Create statsd in realm All + subrealm
        data = {
            'name': 'statsd influx All',
            'address': '192.168.0.101',
            'port': 8125,
            'prefix': 'alignak-statsd',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/statsd', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        statsd_all = resp['_id']

        # Create an influxdb in All B linked to grafana
        data = {
            'name': 'influxdb B',
            'address': '192.168.0.101',
            'port': 8086,
            'database': 'alignak',
            'login': 'alignak',
            'password': 'alignak',
            'prefix': 'my_B',
            'grafana': grafana_all,
            'statsd': statsd_all,
            '_realm': self.realmAll_B
        }
        response = requests.post(self.endpoint + '/influxdb', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Create an influxdb in All A + subrealm liked to grafana
        data = {
            'name': 'influxdb A sub',
            'address': '192.168.0.102',
            'port': 8086,
            'database': 'alignak',
            'login': 'alignak',
            'password': 'alignak',
            'prefix': 'my_A_sub',
            'grafana': grafana_all,
            '_realm': self.realmAll_A,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/influxdb', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # test grafana class and code to create dashboard in grafana
        from alignak_backend.app import app, current_app
        with app.test_request_context():
            grafana_db = current_app.data.driver.db['grafana']
            grafanas = grafana_db.find()
            for grafana in grafanas:
                with requests_mock.mock() as mockreq:
                    ret = [{"id": 1, "orgId": 1, "name": 'alignak-influxdb-influxdb B',
                            "type": "grafana-simple-json-datasource",
                            "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/img/"
                                           "simpleJson_logo.svg",
                            "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                            "password": "", "user": "", "database": "", "basicAuth": True,
                            "basicAuthUser": "", "basicAuthPassword": "", "withCredentials": False,
                            "isDefault": False}]
                    mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                    mockreq.post('http://192.168.0.101:3000/api/datasources',
                                 json={'id': randint(2, 10)})
                    graf = Grafana(grafana)
                    assert len(graf.datasources) == 2
                    assert len(graf.timeseries) == 3
                    assert sorted([ObjectId(self.realmAll_B), ObjectId(self.realmAll_A),
                                   ObjectId(self.realmAll_A1)]) == sorted(graf.timeseries.keys())
                    for ts in graf.timeseries:
                        assert isinstance(ts, ObjectId)
                        assert graf.timeseries[ts]
                        print("TS: %s - %s - %s - %s" % (ts,
                                                         graf.timeseries[ts]['_realm'],
                                                         graf.timeseries[ts]['name'],
                                                         graf.timeseries[ts]['_id']))

                    assert graf.timeseries[ObjectId(self.realmAll_A)]['name'] == 'influxdb A sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['name'] == 'influxdb A sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['ts_prefix'] == \
                        'my_A_sub'
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['statsd_prefix'] == ''
                    assert graf.timeseries[ObjectId(self.realmAll_A1)]['type'] == 'influxdb'

                    assert graf.timeseries[ObjectId(self.realmAll_B)]['name'] == 'influxdb B'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['ts_prefix'] == 'my_B'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['statsd_prefix'] == \
                        'alignak-statsd'
                    assert graf.timeseries[ObjectId(self.realmAll_B)]['type'] == 'influxdb'
                history = mockreq.request_history
                methods = {'POST': 0, 'GET': 0}
                for h in history:
                    methods[h.method] += 1
                # One datasources created because we simulated that on still exists
                assert {'POST': 1, 'GET': 1} == methods

                # Create a dashboard for an host!
                with app.test_request_context():
                    with requests_mock.mock() as mockreq:
                        ret = [{"id": 1, "orgId": 1, "name": 'alignak-influxdb-influxdb B',
                                "type": "grafana-simple-json-datasource",
                                "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/"
                                               "img/simpleJson_logo.svg",
                                "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                                "password": "", "user": "", "database": "", "basicAuth": True,
                                "basicAuthUser": "", "basicAuthPassword": "",
                                "withCredentials": False, "isDefault": True},
                               {"id": 2, "orgId": 1, "name": 'alignak-influxdb-influxdb A sub',
                                "type": "grafana-simple-json-datasource",
                                "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/"
                                               "img/simpleJson_logo.svg",
                                "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                                "password": "", "user": "", "database": "", "basicAuth": True,
                                "basicAuthUser": "", "basicAuthPassword": "",
                                "withCredentials": False, "isDefault": False}]
                        mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                        mockreq.post('http://192.168.0.101:3000/api/datasources',
                                     json={'id': randint(2, 10)})
                        mockreq.post('http://192.168.0.101:3000/api/datasources/db', json='true')
                        mockreq.post('http://192.168.0.101:3000/api/dashboards/db', json='true')
                        graf = Grafana(grafana)
                        for ts in graf.timeseries:
                            print("TS: %s - %s - %s - %s" % (ts,
                                                             graf.timeseries[ts]['_realm'],
                                                             graf.timeseries[ts]['name'],
                                                             graf.timeseries[ts]['_id']))
                        # The host is not in a managed realm
                        assert self.host_srv001['_realm'] == self.realm_all
                        # Must convert to ObjectId because we are not really in Eve :)
                        self.host_srv001['_realm'] = ObjectId(self.host_srv001['_realm'])
                        assert self.host_srv001['_realm'] not in graf.timeseries.keys()
                        assert not graf.create_dashboard(self.host_srv001)

                        assert self.host_srv002['_realm'] == self.realmAll_A1
                        # Must convert to ObjectId because we are not really in Eve :)
                        self.host_srv002['_realm'] = ObjectId(self.host_srv002['_realm'])
                        assert ObjectId(self.host_srv002['_realm']) in graf.timeseries.keys()
                        assert graf.create_dashboard(self.host_srv002)
                        history = mockreq.request_history
                        methods = {'POST': 0, 'GET': 0}
                        for h in history:
                            methods[h.method] += 1
                            if h.method == 'POST':
                                dash = h.json()
                                print("Post response: %s" % dash)
                                # assert len(dash['dashboard']['rows']) == 2
                        assert {'POST': 1, 'GET': 1} == methods

                    # check host and the service are tagged grafana and have the id
                    host_db = current_app.data.driver.db['host']
                    host002 = host_db.find_one({'_id': ObjectId(self.host_srv002['_id'])})
                    assert host002['ls_grafana']
                    assert host002['ls_grafana_panelid'] == 1
                    service_db = current_app.data.driver.db['service']
                    srv002 = service_db.find_one({'_id': ObjectId(self.host_srv002_srv['_id'])})
                    print("Service: %s" % srv002)
                    assert srv002['ls_grafana']
                    assert srv002['ls_grafana_panelid'] == 2

    def test_grafana_connection_error(self):
        """
        This test the connection error of grafana

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        if 'ALIGNAK_BACKEND_PRINT' in os.environ:
            del os.environ['ALIGNAK_BACKEND_PRINT']
        # if 'ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES' in os.environ:
        #     del os.environ['ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES']
        # if 'ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES' in os.environ:
        #     del os.environ['ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES']

        # Create grafana in realm All + subrealm
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        data['name'] = 'grafana 2'
        data['address'] = '192.168.0.102'
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # force request of cron_grafana in the backend
        response = requests.get(self.endpoint + '/cron_grafana')
        resp = response.json()
        print("Response: %s" % resp)
        assert len(resp) == 2
        assert not resp['grafana All']['connection']
        assert not resp['grafana 2']['connection']

        # No more prints ...
        # myfile = open("/tmp/alignak_backend.log")
        # lines = myfile.readlines()
        # for line in lines:
        #     print("- %s" % line)
        # assert 'Connection error to grafana grafana All' in lines[-3]
        # # assert '[cron_grafana] grafana All has no connection' in lines[-4]
        # assert 'Connection error to grafana grafana 2' in lines[-2]
        # # assert '[cron_grafana] grafana 2 has no connection' in lines[-2]

    def test_cron_grafana_service(self):
        """
        This test the grafana cron in the cases:
         * a host has a new service
         * a host does not have ls_perf_data

        :return: None
        """
        headers = {'Content-Type': 'application/json'}
        # Create grafana in realm All + subrealm
        data = {
            'name': 'grafana All',
            'address': '192.168.0.101',
            'apikey': 'xxxxxxxxxxxx1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/grafana', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        grafana_all = resp['_id']

        # Create a graphite in All B linked to grafana
        data = {
            'name': 'graphite All',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': '',
            'grafana': grafana_all,
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # add host 3, without ls_perf_data
        response = requests.get(self.endpoint + '/command', auth=self.auth)
        resp = response.json()
        rc = resp['_items']

        data = json.loads(open('cfg/host_srv001.json').read())
        data['check_command'] = rc[0]['_id']
        if 'realm' in data:
            del data['realm']
        data['_realm'] = self.realm_all
        data['_sub_realm'] = False
        data['ls_last_check'] = int(time.time())
        data['name'] = 'srv003'
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual(resp['_status'], 'OK')
        response = requests.get(self.endpoint + '/host/' + resp['_id'], auth=self.auth)
        host_srv003 = response.json()

        # Add a service for srv003
        data = json.loads(open('cfg/service_srv001_ping.json').read())
        data['host'] = host_srv003
        data['check_command'] = rc[0]['_id']
        data['_realm'] = self.realm_all
        data['_sub_realm'] = False
        data['name'] = 'load'
        data['ls_last_check'] = int(time.time())
        data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                               "load15=0.340;5.000;20.000;0;"
        response = requests.post(self.endpoint + '/service', json=data,
                                 headers=headers, auth=self.auth)

        from alignak_backend.app import app, cron_grafana
        with app.app_context():
            with requests_mock.mock() as mockreq:
                ret = [{"id": 1, "orgId": 1, "name": 'alignak-graphite-graphite B',
                        "type": "grafana-simple-json-datasource",
                        "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/img/"
                                       "simpleJson_logo.svg",
                        "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                        "password": "", "user": "", "database": "", "basicAuth": True,
                        "basicAuthUser": "", "basicAuthPassword": "", "withCredentials": False,
                        "isDefault": False}]
                mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                mockreq.post('http://192.168.0.101:3000/api/datasources',
                             json={'id': randint(2, 10)})
                mockreq.post('http://192.168.0.101:3000/api/dashboards/db', json='true')

                dashboards = json.loads(cron_grafana(engine='jsondumps'))
                print("Dashboards: %s" % dashboards)
                # Created a dashboard for the host srv001 (it has perf_data in the host check)
                assert len(dashboards['grafana All']['created_dashboards']) == 1
                assert dashboards['grafana All']['created_dashboards'][0] == 'srv001'
                # Did not created a dashboard for the host srv003:
                # - no perf_data in the host check!
                # - no service with perf_data!
                # assert len(dashboards['grafana All']['create_dashboard']) == 2
                # assert dashboards['grafana All']['created_dashboards'][1] == 'srv003'

            # add a service with no perf_data in host 3
            data = json.loads(open('cfg/service_srv001_ping.json').read())
            data['host'] = host_srv003['_id']
            data['check_command'] = rc[0]['_id']
            data['_realm'] = self.realm_all
            data['name'] = 'srv1'
            data['ls_last_check'] = int(time.time())
            data['ls_perf_data'] = ""
            requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

            # add a service with no check execution time in host 3
            data = json.loads(open('cfg/service_srv001_ping.json').read())
            data['host'] = host_srv003['_id']
            data['check_command'] = rc[0]['_id']
            data['_realm'] = self.realm_all
            data['name'] = 'srv2'
            data['ls_last_check'] = 0
            data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                                   "load15=0.340;5.000;20.000;0;"
            requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

            # add a service with perf_data and execution time in host 3
            data = json.loads(open('cfg/service_srv001_ping.json').read())
            data['host'] = host_srv003['_id']
            data['check_command'] = rc[0]['_id']
            data['_realm'] = self.realm_all
            data['name'] = 'load'
            data['ls_last_check'] = int(time.time())
            data['ls_perf_data'] = "load1=0.360;15.000;30.000;0; load5=0.420;10.000;25.000;0; " \
                                   "load15=0.340;5.000;20.000;0;"
            requests.post(self.endpoint + '/service', json=data, headers=headers, auth=self.auth)

            with requests_mock.mock() as mockreq:
                ret = [{"id": 1, "orgId": 1, "name": 'alignak-graphite-graphite B',
                        "type": "grafana-simple-json-datasource",
                        "typeLogoUrl": "public/plugins/grafana-simple-json-datasource/src/img/"
                                       "simpleJson_logo.svg",
                        "access": "proxy", "url": "http://127.0.0.1/glpi090/apirest.php",
                        "password": "", "user": "", "database": "", "basicAuth": True,
                        "basicAuthUser": "", "basicAuthPassword": "", "withCredentials": False,
                        "isDefault": False}]
                mockreq.get('http://192.168.0.101:3000/api/datasources', json=ret)
                mockreq.post('http://192.168.0.101:3000/api/datasources',
                             json={'id': randint(2, 10)})
                mockreq.post('http://192.168.0.101:3000/api/dashboards/db', json='true')

                dashboards = json.loads(cron_grafana(engine='jsondumps'))
                assert len(dashboards['grafana All']['created_dashboards']) == 1
                # Created a dashboard including the service
                assert dashboards['grafana All']['created_dashboards'][0] == 'srv003/load'
                # Did not created a dashboard for any other services!
