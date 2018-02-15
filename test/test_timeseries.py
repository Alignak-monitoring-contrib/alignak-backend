#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check preparation of timeseries
"""

from __future__ import print_function
import time
import os
import copy
import shlex
import json
import subprocess
import requests
import requests_mock
import unittest2
from bson.objectid import ObjectId
from alignak_backend.timeseries import Timeseries


class TestTimeseries(unittest2.TestCase):
    """This class test timeseries preparation"""

    maxDiff = None

    @classmethod
    def setUpClass(cls):
        """This method:
          * deletes mongodb database
          * starts the backend with uwsgi
          * log in the backend and get the token
          * add test data to the backend

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
                                  '/tmp/uwsgi.pid', '--logto=/tmp/alignak_backend_tsdb.log'])
        time.sleep(2)

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
        print("Realm All: %s" % cls.realm_all)

        # add more realms
        data = {"name": "All A", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realm_all_A = copy.copy(resp['_id'])

        data = {"name": "All A1", "_parent": cls.realm_all_A}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realm_all_A1 = copy.copy(resp['_id'])

        data = {"name": "All B", "_parent": cls.realm_all}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realm_all_B = copy.copy(resp['_id'])

        data = {"name": "All B1", "_parent": cls.realm_all_B}
        response = requests.post(cls.endpoint + '/realm', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        cls.realm_all_B1 = copy.copy(resp['_id'])

        # Get admin user
        response = requests.get(cls.endpoint + '/user', {"name": "admin"}, auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]['_id']

    @classmethod
    def tearDownClass(cls):
        """Kill uwsgi

        :return: None
        """
        subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
        with open("/tmp/alignak_backend_tsdb.log") as f:
            for line in f:
                print(line)
        os.unlink("/tmp/alignak_backend_tsdb.log")
        time.sleep(2)

    @classmethod
    def tearDown(cls):
        """
        Delete resources in backend

        :return: None
        """
        for resource in ['host', 'service', 'grafana', 'graphite', 'influxdb']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_prepare_data(self):
        """Prepare timeseries from a web perfdata

        :return: None
        """
        item = {
            'host': 'srv001',
            'service': 'check_xxx',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'NGINX OK -  0.161 sec. response time, Active: 25 (Writing: 3 Reading: 0 '
                      'Waiting: 22) ReqPerSec: 58.000 ConnPerSec: 1.200 ReqPerConn: 4.466',
            'long_output': '',
            'perf_data': 'Writing=3;;;; Reading=0;;;; Waiting=22;;;; Active=25;1000;2000;; '
                         'ReqPerSec=58.000000;100;200;; ConnPerSec=1.200000;200;300;; '
                         'ReqPerConn=4.465602;;;; rta=0.083000ms;10.000000;15.000000;0.000000',
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'ReqPerConn',
                    'value': 4.465602,
                    'uom': ''
                },
                {
                    'name': 'Writing',
                    'value': 3,
                    'uom': ''
                },
                {
                    'name': 'Waiting',
                    'value': 22,
                    'uom': ''
                },
                {
                    'name': 'ConnPerSec',
                    'value': 1.2,
                    'uom': ''
                },
                {
                    'name': 'ConnPerSec_warning',
                    'value': 200,
                    'uom': ''
                },
                {
                    'name': 'ConnPerSec_critical',
                    'value': 300,
                    'uom': ''
                },
                {
                    'name': 'Active',
                    'value': 25,
                    'uom': ''
                },
                {
                    'name': 'Active_warning',
                    'value': 1000,
                    'uom': ''
                },
                {
                    'name': 'Active_critical',
                    'value': 2000,
                    'uom': ''
                },
                {
                    'name': 'ReqPerSec',
                    'value': 58,
                    'uom': ''
                },
                {
                    'name': 'ReqPerSec_warning',
                    'value': 100,
                    'uom': ''
                },
                {
                    'name': 'ReqPerSec_critical',
                    'value': 200,
                    'uom': ''
                },
                {
                    'name': 'Reading',
                    'value': 0,
                    'uom': ''
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
                {
                    'name': 'rta',
                    'value': 0.083,
                    'uom': 'ms'
                },
                {
                    'name': 'rta_warning',
                    'value': 10,
                    'uom': 'ms'
                },
                {
                    'name': 'rta_critical',
                    'value': 15,
                    'uom': 'ms'
                },
                {
                    'name': 'rta_min',
                    'value': 0,
                    'uom': 'ms'
                }
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

    def test_prepare_data_special(self):
        """Prepare timeseries from a special perfdata, with
        * name instead numerical value
        * name composed by: string.timestamp

        :return: None
        """
        item = {
            'host': 'srv001',
            'service': 'check_xxx',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'em0:UP (0.0Mbps/0.0Mbps/0.0/0.0/0.0/0.0) (1 UP): OK',
            'long_output': '',
            'perf_data': "cache_descr_names=em0 cache_descr_time=1475663830 "
                         "em0_out_octet.1475670730'=86608341539",
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'cache_descr_time',
                    'value': 1475663830,
                    'uom': ''
                },
                {
                    'name': 'em0_out_octet',
                    'value': 86608341539,
                    'uom': ''
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

    def test_prepare_data_nrpe_checks(self):
        """Prepare timeseries from an NRPE disk

        :return: None
        """
        # Nnrpe check_disk
        item = {
            'host': 'srv001',
            'service': 'check_xxx',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'DISK OK - free space: /tmp 2323 MB (33% inode=64%);',
            'long_output': '',
            # Note the leading space and /
            'perf_data': " /tmp=4660MB;5904;6642;0;7381",
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': '_tmp',
                    'value': 4660,
                    'uom': 'MB'
                },
                {
                    'name': '_tmp_critical',
                    'value': 6642,
                    'uom': 'MB'
                },
                {
                    'name': '_tmp_warning',
                    'value': 5904,
                    'uom': 'MB'
                },
                {
                    'name': '_tmp_min',
                    'value': 0,
                    'uom': 'MB'
                },
                {
                    'name': '_tmp_max',
                    'value': 7381,
                    'uom': 'MB'
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

        # Nnrpe check_root
        item = {
            'host': 'srv001',
            'service': 'check_root',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'DISK OK - free space: / 6468 MB (82% inode=89%);',
            'long_output': '',
            # Note the leading space and /
            'perf_data': " /=1403MB;6653;7485;0;8317",
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': '_',
                    'value': 1403,
                    'uom': 'MB'
                },
                {
                    'name': '__critical',
                    'value': 7485,
                    'uom': 'MB'
                },
                {
                    'name': '__warning',
                    'value': 6653,
                    'uom': 'MB'
                },
                {
                    'name': '__min',
                    'value': 0,
                    'uom': 'MB'
                },
                {
                    'name': '__max',
                    'value': 8317,
                    'uom': 'MB'
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

    def test_prepare_data_cumulative(self):
        """Prepare timeseries from cumulative counters
            PROCESS_SERVICE_CHECK_RESULT;ek3022fdj-00007;Maintenance;0;Application started
            |'MaintenanceOff'=197c 'MaintenanceOn'=1083c 'skAppCritical'=2c 'skAppKoRestart'=1c

        :return: None
        """
        # Nnrpe check_disk
        item = {
            'host': 'srv001',
            'service': 'maintenance',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'Check output',
            'long_output': '',
            # Note the leading space and /
            'perf_data': "'MaintenanceOff'=197c 'MaintenanceOn'=1083c",
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'MaintenanceOff',
                    'value': 197,
                    'uom': 'c'
                },
                {
                    'name': 'MaintenanceOn',
                    'value': 1083,
                    'uom': 'c'
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

    def test_prepare_special_formatted(self):
        """Prepare timeseries from a special perfdata, with
        * : in name
        * % in name

        :return: None
        """
        item = {
            'host': 'srv001',
            'service': 'nsca_cpu',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            '_overall_state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'OK All 1 drive(s) are ok',
            'long_output': '',
            'perf_data': "'C:'=13.19606GB;29.99853;33.99833;0;39.99804 "
                         "'C:%'=33%;75;85;0;100 "
                         "'C:_pct'=33%;75;85;0;100",
            '_realm': 'All.Propieres'
        }

        ret = Timeseries.prepare_data(item)
        reference = {
            'data': [
                {
                    'name': 'C',
                    'value': 13.19606,
                    'uom': 'GB'
                },
                {
                    'name': 'C_warning',
                    'value': 29.99853,
                    'uom': 'GB'
                },
                {
                    'name': 'C_critical',
                    'value': 33.99833,
                    'uom': 'GB'
                },
                {
                    'name': 'C_min',
                    'value': 0,
                    'uom': 'GB'
                },
                {
                    'name': 'C_max',
                    'value': 39.99804,
                    'uom': 'GB'
                },
                {
                    'name': 'C_pct',
                    'value': 33,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_warning',
                    'value': 75,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_critical',
                    'value': 85,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_min',
                    'value': 0,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_max',
                    'value': 100,
                    'uom': '%'
                },
                {
                    'name': 'C_pct',
                    'value': 33,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_warning',
                    'value': 75,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_critical',
                    'value': 85,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_min',
                    'value': 0,
                    'uom': '%'
                },
                {
                    'name': 'C_pct_max',
                    'value': 100,
                    'uom': '%'
                },
                {'name': 'alignak_state_id', 'uom': '', 'value': 0},
                {'name': 'alignak_overall_state_id', 'uom': '', 'value': 0},
            ]
        }
        self.assertItemsEqual(reference['data'], ret['data'])

    def test_generate_realm_prefix(self):
        """Test generate realm prefix when have many levels

        :return: None
        """
        # print("***Realm All: %s" % self.realm_all)
        headers = {'Content-Type': 'application/json'}
        data = {
            'name': 'realm A',
            '_parent': self.realm_all
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_a = resp['_id']

        data = {
            'name': 'realm B',
            '_parent': self.realm_all
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_b = resp['_id']

        data = {
            'name': 'realm A1',
            '_parent': realm_a
        }
        response = requests.post(self.endpoint + '/realm', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        realm_a1 = resp['_id']

        from alignak_backend.app import app
        with app.test_request_context():
            prefix = Timeseries.get_realms_prefix(ObjectId(self.realm_all))
            self.assertEqual(prefix, 'All')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_a))
            self.assertEqual(prefix, 'All.realm A')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_b))
            self.assertEqual(prefix, 'All.realm B')
            prefix = Timeseries.get_realms_prefix(ObjectId(realm_a1))
            self.assertEqual(prefix, 'All.realm A.realm A1')

    def test_timeseries_realm_all_sub(self):
        # pylint: disable=too-many-locals
        """Test with 2 graphites + 1 infuxdb in realm All + sub_realm true.
        We send data in timeseries class and catch the request to graphite and influxdb.

        Note that the realms_prefix (True/False) feature cannot be tested! This because the prefix
        is prepended when data are sent to Graphite!

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # add graphite 001, realm All, with a prefix but no realms prefix for the metrics
        data = {
            'name': 'graphite 001',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'graphite1',
            'realms_prefix': False,
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        graphite_001 = resp['_id']

        # add graphite 002, realm All, no sub-realms
        data = {
            'name': 'graphite 002',
            'carbon_address': '192.168.0.102',
            'graphite_address': '192.168.0.102',
            'prefix': '',
            'realms_prefix': True,
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        graphite_002 = resp['_id']

        # add influxdb 001, realm All
        data = {
            'name': 'influxdb 001',
            'address': '192.168.0.103',
            'login': 'alignak',
            'password': 'alignak',
            'database': 'alignak',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/influxdb', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        influxdb_001 = resp['_id']

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        data['_sub_realm'] = True
        data['name'] = 'ping1'
        response = requests.post(self.endpoint + '/command', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        command_ping = resp['_id']

        # add host in realm All
        data = {
            'name': 'srv001',
            'address': '127.0.0.1',
            'check_command': command_ping,
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        host_001 = resp['_id']

        # add host in realm All A
        data = {
            'name': 'srv002',
            'address': '127.0.0.1',
            'check_command': command_ping,
            '_realm': self.realm_all_A,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        host_002 = resp['_id']

        # add host in realm All A1
        data = {
            'name': 'srv003',
            'address': '127.0.0.1',
            'check_command': command_ping,
            '_realm': self.realm_all_A1,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        host_003 = resp['_id']

        # === Test now with an host in realm All ===
        # add logcheckresult for host001
        # Metrics sent to Graphite 1, Graphite 2 and InfluxDB
        item = {
            'host': ObjectId(host_001),
            'host_name': 'srv001',
            'service': None,
            'service_name': '',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
            'long_output': '',
            'perf_data': "rta=74.827003ms;100.000000;110.000000;0.000000 pl=0%;10;;0",
            '_realm': ObjectId(self.realm_all),
            '_sub_realm': False
        }
        from alignak_backend.app import app, current_app
        with app.test_request_context():
            # Drop the collection before posting the log check result
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            timeseriesretention_db.drop()

            # test with timeseries not available, it must be quick (< 3 seconds), because have
            # 2 graphites and 1 influx, so (2 + 1) * 1 second timeout * 2 (code execution between
            # each tries send to timeseries)
            # Plus some time because the former test (test_sanitized) also has some TSDB ...
            # so 12 seconds
            time_begin = time.time()
            Timeseries.after_inserted_logcheckresult([item])
            execution_time = time.time() - time_begin
            assert execution_time < 12

            # check data in timeseriesretention
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            retentions = timeseriesretention_db.find()
            retention_data = []
            for retention in retentions:
                retention_data.append({
                    'realm': retention['realm'],
                    'name': retention['name'],
                    'uom': retention['uom'],
                    'service': retention['service'],
                    'graphite': retention['graphite'],
                    'influxdb': retention['influxdb'],
                    'host': retention['host'],
                    'value': retention['value']
                })
            ref = [
                # InfluxDB
                {'influxdb': ObjectId(influxdb_001), 'value': u'3', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'74.827003', 'host': u'srv001',
                 'realm': u'All', 'name': u'rta', 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100', 'host': u'srv001',
                 'realm': u'All', 'name': u'rta_warning', 'service': u'', 'graphite': None,
                 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'110', 'host': u'srv001',
                 'realm': u'All', 'name': u'rta_critical', 'service': u'', 'graphite': None,
                 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'rta_min', 'service': u'', 'graphite': None,
                 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'pl', 'service': u'', 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'10', 'host': u'srv001',
                 'realm': u'All', 'name': u'pl_warning', 'service': u'', 'graphite': None,
                 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'pl_min', 'service': u'', 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100', 'host': u'srv001',
                 'realm': u'All', 'name': u'pl_max', 'service': u'', 'graphite': None, 'uom': u'%'},

                # Graphite 001
                {'influxdb': None, 'value': u'3', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'74.827003', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta', 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_critical', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_min', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All', 'name': u'pl',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_min', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_max', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},

                # Graphite 002
                {'influxdb': None, 'value': u'3', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'srv001',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'74.827003', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta', 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_warning', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_critical', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All',
                 'name': u'rta_min', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All', 'name': u'pl',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_warning', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_min', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'srv001', 'realm': u'All',
                 'name': u'pl_max', 'service': u'',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
            ]

            self.assertItemsEqual(ref, retention_data)
            timeseriesretention_db.drop()

        # === Test now with an host in realm All A1 ===
        # add logcheckresult for host003
        # Metrics sent to Graphite 1 and InfluxDB. No Graphite 2 ...
        item = {
            'host': ObjectId(host_003),
            'host_name': 'srv003',
            'service': None,
            'service_name': '',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            # '_overall_state_id': 0, not existing for test purpose
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
            'long_output': '',
            'perf_data': "rta=32.02453ms;100.000000;110.000000;0.000000 pl=0%;10;;0",
            '_realm': ObjectId(self.realm_all_A1),
            '_sub_realm': False

        }
        with app.test_request_context():
            # test with timeseries not available, it must be quick (< 3 seconds), because have
            # 2 graphites and 1 influx, so (2 + 1) * 1 second timeout * 2 (code execution between
            # each tries send to timeseries)
            time_begin = time.time()
            Timeseries.after_inserted_logcheckresult([item])
            execution_time = time.time() - time_begin
            assert execution_time < 6

            # check data in timeseriesretention
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            retentions = timeseriesretention_db.find()
            retention_data = []
            for retention in retentions:
                retention_data.append({
                    'realm': retention['realm'],
                    'name': retention['name'],
                    'uom': retention['uom'],
                    'service': retention['service'],
                    'graphite': retention['graphite'],
                    'influxdb': retention['influxdb'],
                    'host': retention['host'],
                    'value': retention['value']
                })

            ref = [
                # Graphite 001
                {'influxdb': None, 'value': u'3', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_overall_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'32.02453', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'rta', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'rta_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'rta_critical', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'rta_min', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},

                {'influxdb': None, 'value': u'0', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl', 'service': u'', 'graphite': ObjectId(graphite_001),
                 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_min', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_max', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},

                # Influx 001
                {'influxdb': ObjectId(influxdb_001), 'value': u'3', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_overall_state_id',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'alignak_state_id', 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'32.02453',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta', 'service': u'',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta_warning',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'110',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta_critical',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'rta_min', 'service': u'', 'graphite': None,
                 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl', 'service': u'', 'graphite': None,
                 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'10',
                 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_warning', 'service': u'', 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl_min', 'service': u'', 'graphite': None,
                 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'pl_max',
                 'service': u'', 'graphite': None, 'uom': u'%'}
            ]
            self.assertItemsEqual(ref, retention_data)
            timeseriesretention_db.drop()

        # === Add a graphite with StatsD in realm all A1 + sub_realm false ===
        # add statsd
        data = {
            'name': 'statsd 001',
            'address': '192.168.0.1',
            'port': '8125',
            'prefix': 'statsd',
            '_realm': self.realm_all_A,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/statsd', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        statsd = resp['_id']

        # This Graphite has a StatsD in front-end and a specific prefix
        # add graphite 003
        data = {
            'name': 'graphite 003',
            'carbon_address': '192.168.0.104',
            'graphite_address': '192.168.0.104',
            'statsd': statsd,
            'prefix': 'my-prefix',
            '_realm': self.realm_all_A1,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        # graphite_003 = resp['_id']

        # Test now with a host in realm All A1
        # add logcheckresult for host003
        # Metrics sent to Graphite 1, InfluxDB and Graphite 3 ... no Graphite 2
        item = {
            'host': ObjectId(host_003),
            'host_name': 'srv003',
            'service': None,
            'service_name': '',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
            'long_output': '',
            'perf_data': "rta=32.02453ms;100.000000;110.000000 pl=0%;10;;",
            '_realm': ObjectId(self.realm_all_A1),
            '_sub_realm': True
        }
        with app.test_request_context():
            # test with timeseries not available, it must be quick (< 3 seconds), because have
            # 2 graphites and 1 influx, so (2 + 1) * 1 second timeout * 2 (code execution between
            # each tries send to timeseries)
            time_begin = time.time()
            Timeseries.after_inserted_logcheckresult([item])
            execution_time = time.time() - time_begin
            assert execution_time < 6

            # check data in timeseriesretention
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            retentions = timeseriesretention_db.find()
            retention_data = []
            for retention in retentions:
                retention_data.append({
                    'realm': retention['realm'],
                    'name': retention['name'],
                    'uom': retention['uom'],
                    'service': retention['service'],
                    'graphite': retention['graphite'],
                    'influxdb': retention['influxdb'],
                    'host': retention['host'],
                    'value': retention['value']
                })

            ref = [
                # Graphite 001
                {'influxdb': None, 'value': u'3', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_overall_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'32.02453', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'rta', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'rta_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'rta_critical', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl', 'service': u'', 'graphite': ObjectId(graphite_001),
                 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_min', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'srv003', 'realm': u'All.All A.All A1',
                 'name': u'pl_max', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},

                # Graphite 003
                # No data in the retention for this Graphite because it is using StatsD
                # that is not able to detect if connection is available (UDP)!

                # Influx 001
                {'influxdb': ObjectId(influxdb_001), 'value': u'3', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_overall_state_id', 'service': u'',
                 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'alignak_state_id', 'service': u'',
                 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'32.02453',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta', 'service': u'',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta_warning',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'110',
                 'host': u'srv003', 'realm': u'All.All A.All A1', 'name': u'rta_critical',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl', 'service': u'', 'graphite': None,
                 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'10', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl_warning', 'service': u'',
                 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl_min', 'service': u'', 'graphite': None,
                 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100', 'host': u'srv003',
                 'realm': u'All.All A.All A1', 'name': u'pl_max', 'service': u'', 'graphite': None,
                 'uom': u'%'}
            ]
            self.assertItemsEqual(ref, retention_data)
            timeseriesretention_db.drop()

        # Test now with a host in realm All A
        # add logcheckresult of host002
        item = {
            'host': ObjectId(host_002),
            'host_name': 'srv002',
            'service': None,
            'service_name': '',
            'state': 'OK',
            'state_type': 'HARD',
            'state_id': 0,
            'acknowledged': False,
            'last_check': int(time.time()),
            'last_state': 'OK',
            'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
            'long_output': '',
            'perf_data': "rta=32.02453ms;100.000000;110.000000 pl=0;10",
            '_realm': ObjectId(self.realm_all_A),
            '_sub_realm': True
        }
        with app.test_request_context():
            # Drop the collection before posting the log check result
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            timeseriesretention_db.drop()

            # test with timeseries not available, it must be quick (< 3 seconds), because have
            # 3 graphites and 1 influx, so (3 + 1) * 1 second timeout * 2 (code execution
            # between each tries send to timeseries)
            time_begin = time.time()
            Timeseries.after_inserted_logcheckresult([item])
            execution_time = time.time() - time_begin
            assert execution_time < 8

            # check data in timeseriesretention
            retentions = timeseriesretention_db.find()
            retention_data = []
            for retention in retentions:
                retention_data.append({
                    'realm': retention['realm'],
                    'name': retention['name'],
                    'service': retention['service'],
                    'uom': retention['uom'],
                    'graphite': retention['graphite'],
                    'influxdb': retention['influxdb'],
                    'host': retention['host'],
                    'value': retention['value']
                })

            ref = [
                # Graphite 001
                {'influxdb': None, 'value': u'3', 'host': u'srv002',
                 'realm': u'All.All A', 'name': u'alignak_overall_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'srv002',
                 'realm': u'All.All A', 'name': u'alignak_state_id', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'32.02453', 'host': u'srv002',
                 'realm': u'All.All A', 'name': u'rta', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'srv002', 'realm': u'All.All A',
                 'name': u'rta_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'srv002', 'realm': u'All.All A',
                 'name': u'rta_critical', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'srv002', 'realm': u'All.All A',
                 'name': u'pl', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'10', 'host': u'srv002', 'realm': u'All.All A',
                 'name': u'pl_warning', 'service': u'',
                 'graphite': ObjectId(graphite_001), 'uom': u''},

                # Graphite 002
                # Nothing for Graphite 2 because it is not sub-realm!

                # Influx 001
                {'influxdb': ObjectId(influxdb_001), 'value': u'3',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'alignak_overall_state_id',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'alignak_state_id',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'32.02453',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'rta', 'service': u'',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'rta_warning',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'110',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'rta_critical',
                 'service': u'', 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'pl', 'service': u'',
                 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'10',
                 'host': u'srv002', 'realm': u'All.All A', 'name': u'pl_warning',
                 'service': u'', 'graphite': None, 'uom': u''}
            ]
            self.assertItemsEqual(ref, retention_data)
            timeseriesretention_db.drop()

    def test_sanitized_host_service_names(self):
        # pylint: disable=too-many-locals
        """Test that host and service names are sanitized before sending date

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # add graphite 001, realm All, with a prefix
        data = {
            'name': 'graphite 001 bis',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'graphite1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        graphite_001 = resp['_id']

        # add graphite 002, realm All, no sub-realms
        data = {
            'name': 'graphite 002 bis',
            'carbon_address': '192.168.0.102',
            'graphite_address': '192.168.0.102',
            'prefix': '',
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        graphite_002 = resp['_id']

        # add influxdb 001, realm All
        data = {
            'name': 'influxdb 001 bis',
            'address': '192.168.0.103',
            'login': 'alignak',
            'password': 'alignak',
            'database': 'alignak',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/influxdb', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        influxdb_001 = resp['_id']

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        data['_sub_realm'] = True
        data['name'] = 'ping2'
        response = requests.post(self.endpoint + '/command', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        command_ping = resp['_id']

        # add host in realm All
        data = {
            'name': 'My host',
            'address': '127.0.0.1',
            'check_command': command_ping,
            '_realm': self.realm_all,
            '_sub_realm': False
        }
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        host_id = resp['_id']

        from alignak_backend.app import app, current_app
        with app.test_request_context():
            # Drop the collection before posting the log check result
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            timeseriesretention_db.drop()

            # add a service for this host
            data = {
                'name': 'My service',
                'host': host_id,
                'check_command': command_ping,
                '_realm': self.realm_all,
                '_sub_realm': False
            }
            response = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                     auth=self.auth)
            resp = response.json()
            self.assertEqual('OK', resp['_status'], resp)
            service_id = resp['_id']

            # === Test now with an host in realm All ===
            # add logcheckresult for host001
            # Metrics sent to Graphite 1, Graphite 2 and InfluxDB
            item = {
                'host': ObjectId(host_id),
                'host_name': 'My host',
                'service': ObjectId(service_id),
                'service_name': 'My service',
                'state': 'WARNING',
                'state_type': 'HARD',
                'state_id': 0,
                # '_overall_state_id': 0,
                'acknowledged': False,
                'last_check': int(time.time()),
                'last_state': 'OK',
                'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
                'long_output': '',
                'perf_data': "rta=74.827003ms;100.000000;110.000000;0.000000 pl=0%;10;;0",
                '_realm': ObjectId(self.realm_all),
                '_sub_realm': False
            }

            # test with timeseries not available, it must be quick (< 3 seconds), because have
            # 2 graphites and 1 influx, so (2 + 1) * 1 second timeout * 2 (code execution between
            # each tries send to timeseries)
            time_begin = time.time()
            Timeseries.after_inserted_logcheckresult([item])
            execution_time = time.time() - time_begin
            assert execution_time < 6

            # check data in timeseriesretention
            retentions = timeseriesretention_db.find()
            retention_data = []
            for retention in retentions:
                retention_data.append({
                    'realm': retention['realm'],
                    'name': retention['name'],
                    'uom': retention['uom'],
                    'service': retention['service'],
                    'graphite': retention['graphite'],
                    'influxdb': retention['influxdb'],
                    'host': retention['host'],
                    'value': retention['value']
                })
            ref = [
                # InfluxDB
                {'influxdb': ObjectId(influxdb_001), 'value': u'1',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_total',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_not_monitored',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_flapping',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_acknowledged',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_in_downtime',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'1',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_soft',
                 'service': u'', 'graphite': None, 'uom': u''},

                {'influxdb': ObjectId(influxdb_001), 'value': u'1',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_total',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_flapping',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_not_monitored',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_acknowledged',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_in_downtime',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_soft',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'1',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_hard',
                 'service': u'', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0',
                 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_soft',
                 'service': u'', 'graphite': None, 'uom': u''},

                {'influxdb': ObjectId(influxdb_001), 'value': u'3', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'My_service', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'My_service', 'graphite': None, 'uom': u''},
                {'influxdb': ObjectId(influxdb_001), 'value': u'74.827003', 'host': u'My_host',
                 'realm': u'All', 'name': u'rta', 'service': u'My_service',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100', 'host': u'My_host',
                 'realm': u'All', 'name': u'rta_warning', 'service': u'My_service',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'110', 'host': u'My_host',
                 'realm': u'All', 'name': u'rta_critical', 'service': u'My_service',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'rta_min', 'service': u'My_service',
                 'graphite': None, 'uom': u'ms'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'pl', 'service': u'My_service',
                 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'10', 'host': u'My_host',
                 'realm': u'All', 'name': u'pl_warning', 'service': u'My_service',
                 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'pl_min', 'service': u'My_service',
                 'graphite': None, 'uom': u'%'},
                {'influxdb': ObjectId(influxdb_001), 'value': u'100', 'host': u'My_host',
                 'realm': u'All', 'name': u'pl_max', 'service': u'My_service',
                 'graphite': None, 'uom': u'%'},

                # Graphite 001
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_total',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_flapping',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_not_monitored',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_acknowledged',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_in_downtime',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},

                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_total',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_flapping',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_not_monitored',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_acknowledged',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_in_downtime',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_hard',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_soft',
                 'service': u'', 'graphite': ObjectId(graphite_001), 'uom': u''},

                {'influxdb': None, 'value': u'3', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'My_service', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'My_service', 'graphite': ObjectId(graphite_001), 'uom': u''},
                {'influxdb': None, 'value': u'74.827003', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_warning', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_critical', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_min', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_warning', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_min', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_max', 'service': u'My_service',
                 'graphite': ObjectId(graphite_001), 'uom': u'%'},

                # Graphite 002
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_total',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_flapping',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_not_monitored',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_acknowledged',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_in_downtime',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_down_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_up_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'hosts_unreachable_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},

                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_total',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_flapping',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_not_monitored',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_acknowledged',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_in_downtime',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_ok_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_warning_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_critical_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unreachable_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'1', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_hard',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'alignak_livesynthesis',
                 'realm': u'All', 'name': u'services_unknown_soft',
                 'service': u'', 'graphite': ObjectId(graphite_002), 'uom': u''},

                {'influxdb': None, 'value': u'3', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_overall_state_id',
                 'service': u'My_service', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'0', 'host': u'My_host',
                 'realm': u'All', 'name': u'alignak_state_id',
                 'service': u'My_service', 'graphite': ObjectId(graphite_002), 'uom': u''},
                {'influxdb': None, 'value': u'74.827003', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'100', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_warning', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'110', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_critical', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'rta_min', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'ms'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'10', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_warning', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'0', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_min', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
                {'influxdb': None, 'value': u'100', 'host': u'My_host', 'realm': u'All',
                 'name': u'pl_max', 'service': u'My_service',
                 'graphite': ObjectId(graphite_002), 'uom': u'%'},
            ]

            self.assertItemsEqual(ref, retention_data)
            timeseriesretention_db.drop()

    def test_not_process_perf_data(self):
        # pylint: disable=too-many-locals
        """Test that host and service names can be configured with not_process_perf_data

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # add graphite 001, realm All, with a prefix
        data = {
            'name': 'graphite no perf',
            'carbon_address': '192.168.0.101',
            'graphite_address': '192.168.0.101',
            'prefix': 'graphite1',
            '_realm': self.realm_all,
            '_sub_realm': True
        }
        response = requests.post(self.endpoint + '/graphite', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Add command
        data = json.loads(open('cfg/command_ping.json').read())
        data['_realm'] = self.realm_all
        data['_sub_realm'] = True
        data['name'] = 'ping no perf'
        response = requests.post(self.endpoint + '/command', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        command_ping = resp['_id']

        # add host in realm All
        data = {
            'name': 'My host with no perf',
            'address': '127.0.0.1',
            'check_command': command_ping,
            '_realm': self.realm_all,
            '_sub_realm': False,
            'process_perf_data': False
        }
        response = requests.post(self.endpoint + '/host', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        host_id = resp['_id']

        # add a service for this host
        data = {
            'name': 'My service with no perf',
            'host': host_id,
            'check_command': command_ping,
            '_realm': self.realm_all,
            '_sub_realm': False,
            'process_perf_data': False
        }
        response = requests.post(self.endpoint + '/service', json=data, headers=headers,
                                 auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)
        service_id = resp['_id']

        from alignak_backend.app import app, current_app
        with app.test_request_context():
            # Drop the collection before posting the log check result
            timeseriesretention_db = current_app.data.driver.db['timeseriesretention']
            timeseriesretention_db.drop()

            # add a logcheckresult for the host
            item = {
                'host': ObjectId(host_id),
                'host_name': 'My host',
                'service': None,
                'service_name': '',
                'state': 'WARNING',
                'state_type': 'HARD',
                'state_id': 0,
                # '_overall_state_id': 0,
                'acknowledged': False,
                'last_check': int(time.time()),
                'last_state': 'OK',
                'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
                'long_output': '',
                'perf_data': "rta=74.827003ms;100.000000;110.000000;0.000000 pl=0%;10;;0",
                '_realm': ObjectId(self.realm_all),
                '_sub_realm': False
            }
            Timeseries.after_inserted_logcheckresult([item])

            # add a logcheckresult for the service
            item = {
                'host': ObjectId(host_id),
                'host_name': 'My host',
                'service': ObjectId(service_id),
                'service_name': 'My service',
                'state': 'WARNING',
                'state_type': 'HARD',
                'state_id': 0,
                # '_overall_state_id': 0,
                'acknowledged': False,
                'last_check': int(time.time()),
                'last_state': 'OK',
                'output': 'PING OK - Packet loss = 0%, RTA = 0.08 ms',
                'long_output': '',
                'perf_data': "rta=74.827003ms;100.000000;110.000000;0.000000 pl=0%;10;;0",
                '_realm': ObjectId(self.realm_all),
                '_sub_realm': False
            }
            Timeseries.after_inserted_logcheckresult([item])

            # check data in timeseriesretention
            retentions = timeseriesretention_db.find()
            # No metrics exist!
            assert retentions.count() == 0

            timeseriesretention_db.drop()
