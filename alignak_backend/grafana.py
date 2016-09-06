#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.grafana`` module

    This module manages the grafana dashboard / graphs
"""
from __future__ import print_function
from future.utils import iteritems
import requests
from flask import current_app
from eve.methods.patch import patch_internal
from alignak_backend.perfdata import PerfDatas
from alignak_backend.timeseries import Timeseries


class Grafana(object):
    """
        Grafana class
    """
    def __init__(self):
        self.api_key = current_app.config.get('GRAFANA_APIKEY')
        self.host = current_app.config.get('GRAFANA_HOST')
        self.port = str(current_app.config.get('GRAFANA_PORT'))
        self.dashboard_template = current_app.config.get('GRAFANA_TEMPLATE_DASHBOARD')
        self.graphite = current_app.config.get('GRAPHITE_HOST')
        self.carbon = current_app.config.get('CARBON_HOST')
        self.influxdb = current_app.config.get('INFLUXDB_HOST')
        datasource = None
        if self.influxdb:
            datasource = self.get_datasource('influxdb')
        elif self.graphite:
            datasource = self.get_datasource('graphite')
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = None

    def create_dashboard(self, host_id):  # pylint: disable=too-many-locals
        """
        Create / update a dashboard in Grafana

        :param host_id: id of the host
        :type host_id: str
        :return: None
        """
        if not self.datasource:
            return
        headers = {"Authorization": "Bearer " + self.api_key}

        host_db = current_app.data.driver.db['host']
        service_db = current_app.data.driver.db['service']
        command_db = current_app.data.driver.db['command']

        host = host_db.find_one({'_id': host_id})
        hostname = host['name']
        command = command_db.find_one({'_id': host['check_command']})
        command_name = command['name']

        rows = []
        targets = []
        refids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
        perfdata = PerfDatas(host['ls_perf_data'])
        num = 0
        for measurement in perfdata.metrics:
            fields = perfdata.metrics[measurement].__dict__
            mytarget = Timeseries.get_realms_prefix(host['_realm']) + '.' + hostname
            mytarget += '.' + fields['name']
            targets.append(self.generate_target(fields['name'], {"host": hostname}, refids[num],
                                                mytarget))
            num += 1
        if len(targets) > 0:
            rows.append(self.generate_row(command_name, targets))
            if host['ls_last_check'] > 0:
                # Update host live state
                data = {
                    "ls_grafana": True,
                    "ls_grafana_panelid": 1
                }
                lookup = {"_id": host['_id']}
                patch_internal('host', data, False, False, **lookup)

        # now get services
        services = service_db.find({'host': host_id})
        for service in services:
            if service['ls_last_check'] > 0:

                perfdata = PerfDatas(service['ls_perf_data'])
                targets = []
                num = 0
                for measurement in perfdata.metrics:
                    fields = perfdata.metrics[measurement].__dict__
                    mytarget = Timeseries.get_realms_prefix(host['_realm']) + '.' + hostname
                    mytarget += '.' + service['name'] + '.' + fields['name']
                    targets.append(self.generate_target(fields['name'],
                                                        {"host": hostname,
                                                         "service": service['name']}, refids[num],
                                                        mytarget))
                    num += 1
                if len(targets) > 0:
                    rows.append(self.generate_row(service['name'], targets))
                    # Update service live state
                    data = {
                        "ls_grafana": True,
                        "ls_grafana_panelid": len(rows)
                    }
                    lookup = {"_id": service['_id']}
                    patch_internal('service', data, False, False, **lookup)

        self.dashboard_template['id'] = None
        self.dashboard_template['title'] = "host_" + hostname
        self.dashboard_template['rows'] = rows

        data = {
            "dashboard": self.dashboard_template,
            "overwrite": True
        }
        requests.post('http://' + self.host + ':' + self.port + '/api/dashboards/db', json=data,
                      headers=headers)

    def get_datasource(self, dtype):
        """
        Get datasource or create it if not exist

        :param dtype: type of the datasource: influxdb | graphite
        :type dtype: str
        :return: name of the datasource
        :rtype: str
        """
        headers = {"Authorization": "Bearer " + self.api_key}
        response = requests.get('http://' + self.host + ':' + self.port + '/api/datasources',
                                headers=headers)
        resp = response.json()
        if dtype == 'influxdb':
            ds_url = self.influxdb
        elif dtype == 'graphite':
            ds_url = self.graphite
        for datasource in iter(resp):
            if datasource['type'] == dtype and ds_url in datasource['url']:
                return datasource['name']
        # no datasource, create one
        if dtype == 'influxdb':
            data = {
                "name": "influxdb",
                "type": "influxdb",
                "typeLogoUrl": "",
                "access": "proxy",
                "url": "http://" + self.influxdb + ":" +
                       str(current_app.config.get('INFLUXDB_PORT')),
                "password": current_app.config.get('INFLUXDB_PASSWORD'),
                "user": current_app.config.get('INFLUXDB_LOGIN'),
                "database": current_app.config.get('INFLUXDB_DATABASE'),
                "basicAuth": False,
                "basicAuthUser": "",
                "basicAuthPassword": "",
                "withCredentials": False,
                "isDefault": True,
                "jsonData": {}
            }
        elif dtype == 'graphite':
            data = {
                "name": "graphite",
                "type": "graphite",
                "access": "proxy",
                "url": "http://" + self.graphite + ":" +
                       str(current_app.config.get('GRAPHITE_PORT')),
                "basicAuth": False,
                "basicAuthUser": "",
                "basicAuthPassword": "",
                "withCredentials": False,
                "isDefault": True,
                "jsonData": {}
            }
        response = requests.post('http://' + self.host + ':' + self.port + '/api/datasources',
                                 json=data, headers=headers)
        resp = response.json()
        print(resp)
        return dtype

    def generate_target(self, measurement, tags, refid, mytarget):
        """
        Generate target structure for dashboard

        :param measurement: name of measurement
        :type measurement: str
        :param tags: list of tags
        :type tags: list
        :return: dictionary / structure of target (cf API Grafana)
        :rtype: dict
        """
        prepare_tags = []
        for key, value in iteritems(tags):
            data = {
                "key": key,
                "operator": "=",
                "value": value
            }
            if len(prepare_tags) > 0:
                data['condition'] = 'AND'
            prepare_tags.append(data)

        return {
            "dsType": self.datasource,
            "measurement": measurement,
            "resultFormat": "time_series",
            "policy": "default",
            "tags": prepare_tags,
            "groupBy": [
                {
                    "type": "time",
                    "params": ["auto"]
                },
                {
                    "type": "fill",
                    "params": ["null"]
                }
            ],
            "select": [
                [
                    {
                        "type": "field",
                        "params": ["value"]
                    },
                    {
                        "type": "mean",
                        "params": []
                    }
                ]
            ],
            "target": mytarget,
            "refId": refid,
        }

    def generate_row(self, title, targets):
        """
        Generate a row in dashboard

        :param title: Name of the row / graph
        :type title: str
        :param targets: all targets (all measurements in the row/graph)
        :type targets: dict
        :return: the dictionary of the row
        :rtype: dict
        """
        return {
            "title": "Chart",
            "height": "300px",
            "panels": [
                {
                    "title": title,
                    "type": "graph",
                    "span": 12,
                    "fill": 1,
                    "linewidth": 2,
                    "targets": targets,
                    "tooltip": {
                        "shared": True
                    }
                }
            ]
        }
