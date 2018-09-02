#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This test check grafana and create dashboard + graphs
"""

from __future__ import print_function
import os
import json
from pprint import pprint
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


class TestGrafanaDataSource(unittest2.TestCase):
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
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test-grafana'

        os.environ['ALIGNAK_BACKEND_PRINT'] = 'grafana'
        os.environ['ALIGNAK_BACKEND_GRAFANA_DATASOURCE_QUERIES'] = './cfg/grafana_queries.json'
        os.environ['ALIGNAK_BACKEND_GRAFANA_DATASOURCE_TABLES'] = './cfg/grafana_tables.json'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignak_backend.app:app',
                                  '--socket', '0.0.0.0:5000',
                                  '--protocol=http', '--enable-threads', '--pidfile',
                                  '/tmp/uwsgi.pid', '--logto=/tmp/alignak_backend.log'])
        # cls.p = subprocess.Popen(['alignak-backend'])
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
        with open("/tmp/alignak_backend.log") as f:
            for line in f:
                print(line)
        os.unlink("/tmp/alignak_backend.log")
        time.sleep(2)

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
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'UP'
        data['ls_state_type'] = 'HARD'
        data['ls_state_id'] = 0
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
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'OK'
        data['ls_state_type'] = 'HARD'
        data['ls_state_id'] = 0
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
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'DOWN'
        data['ls_state_type'] = 'SOFT'
        data['ls_state_id'] = 1
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
        data['ls_last_check'] = 1234567890  # Fixed timestamp for test
        data['ls_state'] = 'WARNING'
        data['ls_state_type'] = 'SOFT'
        data['ls_state_id'] = 1
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
                         'graphite', 'influxdb']:
            requests.delete(cls.endpoint + '/' + resource, auth=cls.auth)

    def test_grafana_annotations_error(self):
        """
        Get annotations with some errors

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Request some annotations
        # Time frame for the request - whatever, this endpoint do not care about the time frame!!!
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        past = now - timedelta(days=5)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Grafana request for some annotations
        # Error on syntax
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
                # Ignored...
                u'raw': {u'to': u'now', u'from': u'now-6h'}
            },
            # Ignored...
            u'rangeRaw': {u'to': u'now', u'from': u'now-6h'},
            u'annotation': {
                # Request bad query !
                u'query': u'fake',
                # 4 ignored fields...
                u'iconColor': u'rgba(255, 96, 96, 1)',
                u'enable': True,
                u'name': u'Host alerts',
                u'datasource': u'Backend'
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        print(resp)
        assert "_error" in resp
        assert resp["_error"]["message"] == u"Bad format for query: fake. " \
                                            u"Query must be something like endpoint:type:target."

        # Grafana request for some annotations
        # Error on endpoint
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
                # Ignored...
                u'raw': {u'to': u'now', u'from': u'now-6h'}
            },
            # Ignored...
            u'rangeRaw': {u'to': u'now', u'from': u'now-6h'},
            u'annotation': {
                # Request bad query !
                u'query': u'fake:whatever:{srv001}',
                # 4 ignored fields...
                u'iconColor': u'rgba(255, 96, 96, 1)',
                u'enable': True,
                u'name': u'Host alerts',
                u'datasource': u'Backend'
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        print(resp)
        assert "_error" in resp
        assert resp["_error"]["message"] == u"Bad endpoint for query: fake:whatever:{srv001}. " \
                                            u"Only history and livestate are available."

    def test_grafana_history_annotations(self):
        """
        Get annotations from history

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Create an event in the history
        data = {
            'host_name': "test",
            "service_name": "service",
            'user': None,
            'type': 'monitoring.alert',
            'message': "Test event #1 for an alert"
        }
        response = requests.post(self.endpoint + '/history',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Wait 1 second
        time.sleep(1)

        # Create an event in the history
        data = {
            'host_name': "test1",
            'user': None,
            'type': 'monitoring.alert',
            'message': "Test event #2 for an alert"
        }
        response = requests.post(self.endpoint + '/history',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Wait 1 second
        time.sleep(1)

        # Create an event in the history
        data = {
            'host_name': "test2",
            'user': None,
            'type': 'monitoring.alert',
            'message': "Test event #3 for an alert"
        }
        response = requests.post(self.endpoint + '/history',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Wait 1 second
        time.sleep(1)

        # Create an event now in the history
        data = {
            'host_name': "test2",
            'user': None,
            'type': 'monitoring.notification',
            'message': "Test event #4 for an alert"
        }
        response = requests.post(self.endpoint + '/history',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        self.assertEqual('OK', resp['_status'], resp)

        # Request some annotations
        # 1- no results within the time frame
        # Time frame for the request
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # Only one second in the past
        past = now - timedelta(seconds=1)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')
        print("Date from: %s, to: %s" % (range_from, range_to))

        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
                # Ignored...
                u'raw': {u'to': u'now', u'from': u'now-6h'}
            },
            # Ignored...
            u'rangeRaw': {u'to': u'now', u'from': u'now-6h'},
            u'annotation': {
                # Request for alerts of hosts test and test1
                u'query': u'history:monitoring.alert:{test,test1}',
                # 4 ignored fields...
                u'iconColor': u'rgba(255, 96, 96, 1)',
                u'enable': True,
                u'name': u'Host alerts',
                u'datasource': u'Backend'
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        resp = response.json()
        # No items in the response
        print("Response :%s" % resp)
        self.assertEqual(len(resp), 0)

        # Request some annotations
        # 2- with results in the time frame
        # Time frame for the request
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # Five seconds in the past
        past = now - timedelta(seconds=5)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')
        print("Date from: %s, to: %s" % (range_from, range_to))

        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
                # Ignored...
                u'raw': {u'to': u'now', u'from': u'now-6h'}
            },
            # Ignored...
            u'rangeRaw': {u'to': u'now', u'from': u'now-6h'},
            u'annotation': {
                # Request for alerts of hosts test and test1
                u'query': u'history:monitoring.alert:{test,test1}',
                # 4 ignored fields...
                u'iconColor': u'rgba(255, 96, 96, 1)',
                u'enable': True,
                u'name': u'Host alerts',
                u'datasource': u'Backend'
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # Grafana expects a response containing an array of annotation objects
        # in the following format:
        # [
        #   {
        #     annotation: annotation, // The original annotation sent from Grafana.
        #     time: time, // Time since UNIX Epoch in milliseconds. (required)
        #     title: title, // The title for the annotation tooltip. (required)
        #     tags: tags, // Tags for the annotation. (optional)
        #     text: text // Text for the annotation. (optional)
        #   }
        # ]

        # Two items in the response
        self.assertEqual(len(resp), 2)

        # All expected data fields are present
        rsp = resp[0]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "test/service - Test event #1 for an alert")
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["monitoring.alert"])
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "Test event #1 for an alert")

        rsp = resp[1]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "test1 - Test event #2 for an alert")
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["monitoring.alert"])
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "Test event #2 for an alert")

        # Request some annotations
        # 3- for one host only
        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
            },
            u'annotation': {
                # Request for alerts of hosts test and test1
                u'query': u'history:monitoring.alert:test',
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # One item in the response
        self.assertEqual(len(resp), 1)

        # All expected data fields are present
        rsp = resp[0]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "test/service - Test event #1 for an alert")
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["monitoring.alert"])
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "Test event #1 for an alert")

        # Request some annotations
        # 4- for one host specific service
        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
            },
            # Ignored...
            u'annotation': {
                # Request for alerts of the service "service" for the host "test"
                u'query': u'history:monitoring.alert:test:service',
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # One item in the response
        self.assertEqual(len(resp), 1)

        # All expected data fields are present
        rsp = resp[0]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "test/service - Test event #1 for an alert")
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["monitoring.alert"])
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "Test event #1 for an alert")

        # Request some annotations
        # 5- unknown event
        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
            },
            # Ignored...
            u'annotation': {
                # Request for alerts of the host test
                u'query': u'history:fake.event:test',
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # One item in the response
        self.assertEqual(len(resp), 0)

    def test_grafana_livestate_annotations(self):
        """
        Get annotations from livestate

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Request some annotations
        # 2- with results in the time frame
        # Time frame for the request - whatever, this endpoint do not car about the time frame!!!
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # One day in the past
        past = now - timedelta(days=5)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
                # Ignored...
                u'raw': {u'to': u'now', u'from': u'now-6h'}
            },
            # Ignored...
            u'rangeRaw': {u'to': u'now', u'from': u'now-6h'},
            u'annotation': {
                # Request for livestate of hosts srv001
                u'query': u'livestate:whatever:{srv001}',
                # 4 ignored fields...
                u'iconColor': u'rgba(255, 96, 96, 1)',
                u'enable': True,
                u'name': u'Host alerts',
                u'datasource': u'Backend'
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # Grafana expects a response containing an array of annotation objects
        # in the following format:
        # [
        #   {
        #     annotation: annotation, // The original annotation sent from Grafana.
        #     time: time, // Time since UNIX Epoch in milliseconds. (required)
        #     title: title, // The title for the annotation tooltip. (required)
        #     tags: tags, // Tags for the annotation. (optional)
        #     text: text // Text for the annotation. (optional)
        #   }
        # ]

        # One item in the response
        self.assertEqual(len(resp), 1)

        # All expected data fields are present
        rsp = resp[0]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "Server #1")  # Alias
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["t1", "t2"])  # Tags
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "srv001: UP (HARD) - ")     # Live state

        # Request some annotations
        # 3- for one host only
        # Grafana request for some annotations
        data = {
            u'range': {
                u'from': range_from,
                u'to': range_to,
            },
            u'annotation': {
                # Request for livestate of hosts srv001 and srv002
                u'query': u'livestate:whatever:{srv001,srv002}',
            }
        }
        response = requests.post(self.endpoint + '/annotations',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # One item in the response
        self.assertEqual(len(resp), 2)

        # All expected data fields are present
        rsp = resp[0]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "Server #1")  # Alias
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["t1", "t2"])  # Tags
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "srv001: UP (HARD) - ")

        rsp = resp[1]
        self.assertIn('annotation', rsp)
        self.assertEqual(rsp['annotation'], data['annotation'])
        self.assertIn('time', rsp)
        self.assertIn('title', rsp)
        self.assertEqual(rsp['title'], "Server #2")     # Alias
        self.assertIn('tags', rsp)
        self.assertEqual(rsp['tags'], ["t2"])           # Tags
        self.assertIn('text', rsp)
        self.assertEqual(rsp['text'], "srv002: DOWN (SOFT) - ")

    def test_grafana_search(self):
        """
        Get available queries names

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Grafana request for available data:
        data = {}
        response = requests.post(self.endpoint + '/search',
                                 json=data, headers=headers, auth=self.auth)
        resp = response.json()
        # Grafana expects a response containing an array of available queries
        # [
        # "hosts", "hosts up
        # ]

        # One item in the response
        self.assertEqual(len(resp), 11)

        # All expected data fields are present
        self.assertEqual(resp, [u'Hosts', u'Hosts down', u'Hosts problems', u'Hosts unreachable',
                                u'Hosts up',
                                u'Services',
                                u'Services critical', u'Services ok', u'Services problems',
                                u'Services unreachable', u'Services warning'])

    def test_grafana_query_errors(self):
        """
        Get data from the Grafana data source - interface errors

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Time frame for the request - whatever, this endpoint do not car about the time frame!!!
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # One day in the past
        past = now - timedelta(days=5)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # Grafana request for available data:
        #     {
        #       "range": { "from": "2015-12-22T03:06:13.851Z", "to": "2015-12-22T06:48:24.137Z" },
        #       "interval": "5s",
        #       "targets": [
        #         { "refId": "B", "target": "hosts" },
        #         { "refId": "A", "target": "hosts" }
        #       ],
        #       "format": "json",
        #       "maxDataPoints": 2495 //decided by the panel
        #     }

        # --- Missing targets
        data = {
            # Ignored data...
            u'range': {u'from': range_from, u'to': range_to},
            u'interval': "5s",
            u'format': "json",
            u'maxDataPoints': 2495,
            # "targets": [
            #     {"refId": "A", "target": "hosts"},
            #     {"refId": "B", "target": "services"},
            # ],
        }
        response = requests.post(self.endpoint + '/query',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        assert response.status_code == 404
        resp = response.json()
        self.assertEqual(resp['_status'], 'ERR')
        self.assertEqual(resp['_error']['code'], 404)
        self.assertEqual(resp['_error']['message'],
                         u"Only one target is supported by this datasource.")

        # --- Request for more than 1 target
        data = {
            # Ignored data...
            u'range': {u'from': range_from, u'to': range_to},
            u'interval': "5s",
            u'format': "json",
            u'maxDataPoints': 2495,
            # Request 2 targets
            "targets": [
                {"refId": "A", "target": "hosts"},
                {"refId": "B", "target": "services"},
            ],
        }
        response = requests.post(self.endpoint + '/query',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        assert response.status_code == 404
        resp = response.json()
        self.assertEqual(resp['_status'], 'ERR')
        self.assertEqual(resp['_error']['code'], 404)
        self.assertEqual(resp['_error']['message'],
                         u"Only one target is supported by this datasource.")

        # --- Bad formatted query
        data = {
            # Ignored data...
            u'range': {u'from': range_from, u'to': range_to},
            u'interval': "5s",
            u'format': "json",
            u'maxDataPoints': 2495,
            # Bad query
            "targets": [
                {"refId": "A", "target": "host"}
            ],
        }
        response = requests.post(self.endpoint + '/query',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        assert response.status_code == 404
        resp = response.json()
        self.assertEqual(resp['_status'], 'ERR')
        self.assertEqual(resp['_error']['code'], 404)
        self.assertIn("Query must be something like endpoint:field:value.",
                      resp['_error']['message'])

    def test_grafana_query(self):
        """
        Get data from the Grafana data source

        :return: None
        """
        headers = {'Content-Type': 'application/json'}

        # Time frame for the request - whatever, this endpoint do not car about the time frame!!!
        now = datetime.utcnow()
        range_to = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        # One day in the past
        past = now - timedelta(days=5)
        range_from = past.strftime('%a, %d %b %Y %H:%M:%S GMT')

        # --- Request a list of hosts
        data = {
            # Ignored data...
            u'range': {u'from': range_from, u'to': range_to},
            u'interval': "5s",
            u'format': "json",
            u'maxDataPoints': 2495,
            # Useful data:
            "targets": [
                {"refId": "A", "target": "Hosts"}
            ],
        }
        response = requests.post(self.endpoint + '/query',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        resp = response.json()
        pprint(resp)
        self.assertEqual(len(resp), 1)
        rsp = resp[0]

        # All expected data fields are present
        self.assertIn('type', rsp)
        self.assertEqual(rsp["type"], "table")

        self.assertIn('columns', rsp)
        self.assertEqual(len(rsp["columns"]), 14)
        self.assertEqual(
            rsp["columns"], [{u'text': u'Host name', u'type': u'string'},
                             {u'text': u'Alias', u'type': u'string'},
                             {u'text': u'Business impact', u'type': u'integer'},
                             {u'text': u'Tags', u'type': u'list'},
                             {u'text': u'Active checks enabled', u'type': u'boolean'},
                             {u'text': u'Passive checks enabled', u'type': u'boolean'},
                             {u'text': u'Element overall state', u'type': u'integer'},
                             {u'text': u'State', u'type': u'string'},
                             {u'text': u'State identifier', u'type': u'integer'},
                             {u'text': u'State type', u'type': u'string'},
                             {u'text': u'Last check time', u'type': u'integer'},
                             {u'text': u'Acknowledged', u'type': u'boolean'},
                             {u'text': u'Downtimed', u'type': u'boolean'},
                             {u'text': u'Grafana identifier', u'type': u'integer'}])
        for column in rsp["columns"]:
            self.assertIn('text', column)
            self.assertIn('type', column)

        self.assertIn('rows', rsp)
        # 2 hosts
        self.assertEqual(len(rsp["rows"]), 2)
        self.assertEqual(
            rsp['rows'], [
                [u'srv001',
                 u'Server #1',
                 5,
                 u't1,t2',
                 True,
                 True,
                 0,
                 u'UP',
                 0,
                 u'HARD',
                 u'Fri, 13 Feb 2009 23:31:30 GMT',
                 # 1234567890 as a Grafana formated date!
                 False,
                 False,
                 0],
                [u'srv002',
                 u'Server #2',
                 5,
                 u't2',
                 True,
                 True,
                 4,
                 u'DOWN',
                 1,
                 u'SOFT',
                 u'Fri, 13 Feb 2009 23:31:30 GMT',
                 # 1234567890 as a Grafana formated date!
                 False,
                 False,
                 0]
            ])
        for row in rsp["rows"]:
            self.assertEqual(len(row), 14)

        # --- Request a list of services
        data = {
            # Ignored data...
            u'range': {u'from': range_from, u'to': range_to},
            u'interval': "5s",
            u'format': "json",
            u'maxDataPoints': 2495,
            # Useful data:
            "targets": [
                {"refId": "A", "target": "Services"}
            ],
        }
        response = requests.post(self.endpoint + '/query',
                                 json=data, headers=headers, auth=self.auth)
        print("Response: %s" % response)
        resp = response.json()
        pprint(resp)
        self.assertEqual(len(resp), 1)
        rsp = resp[0]

        # All expected data fields are present
        self.assertIn('type', rsp)
        self.assertEqual(rsp["type"], "table")

        self.assertIn('columns', rsp)
        self.assertEqual(len(rsp["columns"]), 15)
        self.assertEqual(
            rsp["columns"], [{u'text': u'Linked host', u'type': u'objectid'},
                             {u'text': u'Service name', u'type': u'string'},
                             {u'text': u'Alias', u'type': u'string'},
                             {u'text': u'Business impact', u'type': u'integer'},
                             {u'text': u'Tags', u'type': u'list'},
                             {u'text': u'Active checks enabled', u'type': u'boolean'},
                             {u'text': u'Passive checks enabled', u'type': u'boolean'},
                             {u'text': u'Element overall state', u'type': u'integer'},
                             {u'text': u'State', u'type': u'string'},
                             {u'text': u'State identifier', u'type': u'integer'},
                             {u'text': u'State type', u'type': u'string'},
                             {u'text': u'Last check time', u'type': u'integer'},
                             {u'text': u'Acknowledged', u'type': u'boolean'},
                             {u'text': u'Downtimed', u'type': u'boolean'},
                             {u'text': u'Grafana identifier', u'type': u'integer'}])
        for column in rsp["columns"]:
            self.assertIn('text', column)
            self.assertIn('type', column)

        self.assertIn('rows', rsp)
        # 2 hosts
        self.assertEqual(len(rsp["rows"]), 2)
        self.assertEqual(
            rsp['rows'], [
                [u'srv001',
                 u'load',
                 u'load',
                 4,
                 u'',
                 True,
                 True,
                 0,
                 u'OK',
                 0,
                 u'HARD',
                 u'Fri, 13 Feb 2009 23:31:30 GMT',
                 # 1234567890 as a Grafana formated date!
                 False,
                 False,
                 0],
                [u'srv002',
                 u'load',
                 u'load',
                 4,
                 u'',
                 True,
                 True,
                 3,
                 u'WARNING',
                 1,
                 u'SOFT',
                 u'Fri, 13 Feb 2009 23:31:30 GMT',
                 # 1234567890 as a Grafana formated date!
                 False,
                 False,
                 0]
            ])
        for row in rsp["rows"]:
            self.assertEqual(len(row), 15)
