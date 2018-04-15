#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.grafana`` module

    This module manages the grafana dashboard / graphs
"""
from __future__ import print_function
import re
from future.utils import iteritems
import requests
from bson.objectid import ObjectId
from flask import current_app
from eve.methods.patch import patch_internal
from alignak_backend.perfdata import PerfDatas
from alignak_backend.timeseries import Timeseries


class Grafana(object):
    """
        Grafana class
    """
    def __init__(self, data):
        self.api_key = data['apikey']
        self.host = data['address']
        self.port = str(data['port'])
        self.name = str(data['name'])
        self.scheme = 'http'
        self.panel_id = 0
        if data['ssl']:
            self.scheme = 'https'
        self.connection = True
        self.dashboard_data = data

        # get the realms of this grafana instance
        realm_db = current_app.data.driver.db['realm']
        realm = realm_db.find_one({'_id': data['_realm']})
        self.realms = [realm['_id']]
        if data['_sub_realm']:
            self.realms.extend(realm['_all_children'])

        # get graphite / influx for each realm of the grafana
        self.timeseries = {}

        graphite_db = current_app.data.driver.db['graphite']
        influxdb_db = current_app.data.driver.db['influxdb']
        statsd_db = current_app.data.driver.db['statsd']

        graphites = graphite_db.find({'grafana': data['_id']})
        for graphite in graphites:
            # A Graphite is linked to me but we do not have any common realm!
            if graphite['_realm'] not in self.realms:
                current_app.logger.error("[grafana-%s] linked graphite %s has no common realm",
                                         self.name, graphite['name'])
                continue

            # Add a statsd_prefix in the graphite if necessary
            graphite['ts_prefix'] = graphite['prefix']
            graphite['statsd_prefix'] = ''
            if graphite['statsd']:
                statsd = statsd_db.find_one({'_id': graphite['statsd']})
                if statsd and statsd['_realm'] not in self.realms:
                    current_app.logger.error("[grafana-%s] linked statsd %s has no common realm",
                                             self.name, statsd['name'])
                    continue
                if statsd and statsd['prefix'] != '':
                    graphite['statsd_prefix'] = statsd['prefix']

            # We already have a TS for the Graphite realm!
            if graphite['_realm'] in self.timeseries:
                current_app.logger.error("[grafana-%s] linked graphite %s has the same realm "
                                         "as a previously registered timeserie",
                                         self.name, graphite['name'])
                continue

            graphite['type'] = 'graphite'
            self.timeseries[graphite['_realm']] = graphite
            if graphite['_sub_realm']:
                realm = realm_db.find_one({'_id': graphite['_realm']})
                for child_realm in realm['_all_children']:
                    if child_realm not in self.realms:
                        current_app.logger.error("[grafana-%s] linked graphite %s, "
                                                 "ignore sub-realm: %s",
                                                 self.name, graphite['name'], child_realm)
                        continue
                    self.timeseries[child_realm] = graphite

        influxdbs = influxdb_db.find({'grafana': data['_id']})
        for influxdb in influxdbs:
            # An InfluxDB is linked to me but we do not have any common realm!
            if influxdb['_realm'] not in self.realms:
                current_app.logger.error("[grafana-%s] linked influxdb %s has no common realm",
                                         self.name, influxdb['name'])
                continue

            # Add a statsd_prefix in the influxdb if necessary
            influxdb['ts_prefix'] = influxdb['prefix']
            influxdb['statsd_prefix'] = ''
            if influxdb['statsd']:
                statsd = statsd_db.find_one({'_id': influxdb['statsd']})
                if statsd and statsd['_realm'] not in self.realms:
                    current_app.logger.error("[grafana-%s] linked statsd %s has no common realm",
                                             self.name, statsd['name'])
                    continue
                if statsd and statsd['prefix'] != '':
                    influxdb['statsd_prefix'] = statsd['prefix']

            # We already have a TS for the InfluxDB realm!
            if influxdb['_realm'] in self.timeseries:
                current_app.logger.error("[grafana-%s] linked influxdb %s has the same realm "
                                         "as a previously registered timeserie",
                                         self.name, influxdb['name'])
                continue

            influxdb['type'] = 'influxdb'
            self.timeseries[influxdb['_realm']] = influxdb
            if influxdb['_sub_realm']:
                realm = realm_db.find_one({'_id': influxdb['_realm']})
                for child_realm in realm['_all_children']:
                    if child_realm not in self.realms:
                        current_app.logger.error("[grafana-%s] linked influxdb %s, "
                                                 "ignore sub-realm: %s",
                                                 self.name, influxdb['name'], child_realm)
                        continue
                    self.timeseries[child_realm] = influxdb

        # Get the Grafana data sources
        self.get_datasources()

    def build_target(self, item, fields):
        """

        :param item: concerned host or service
        :type item: dict
        :param fields: fields of the concerned metric:
                    {'name': u'uptime_minutes',
                     'min': None, 'max': None,
                     'value': 92348,
                     'warning': None, 'critical': None,
                     'uom': u''}
        :type fields: dict
        :return:
        """
        # Find the TS corresponding to the host realm
        ts = self.timeseries[item['_realm']]
        # Add statsd, graphite and realm prefixes
        my_target = ''
        if ts['statsd_prefix'] != '':
            my_target = '$statsd_prefix'
        if ts['ts_prefix'] != '':
            my_target += '.$ts_prefix'
        if ts.get('realms_prefix'):
            my_target += '.' + Timeseries.get_realms_prefix(item['_realm'])
        if 'host' in item:
            my_target += '.' + item['hostname'] + '.' + item['name']
        else:
            my_target += '.' + item['name']
        my_target += '.' + fields['name']
        while my_target.startswith('.'):
            my_target = my_target[1:]

        # Sanitize field name for Graphite:
        # + becomes a _
        my_target = my_target.replace("+", "_")
        # / becomes a -
        my_target = my_target.replace("/", "-")
        # space becomes a _
        my_target = my_target.replace(" ", "_")
        # % becomes _pct
        my_target = my_target.replace("%", "_pct")
        # all character not in [a-zA-Z_-0-9.] is removed
        my_target = re.sub(r'[^a-zA-Z_\-0-9\.\$]', '', my_target)

        # Build path for each metric
        targets = {'main': {'name': fields['name'], 'target': my_target}}
        overrides = []
        if fields['warning'] is not None:
            targets.update({'warning': {'name': fields['name'] + ' (w)',
                                        'target': my_target + '_warning'}})
            overrides.append({'alias': fields['name'] + ' (w)',
                              'fill': 0, 'legend': False, 'color': '#CCA300'})

        if fields['critical'] is not None:
            targets.update({'critical': {'name': fields['name'] + ' (c)',
                                         'target': my_target + '_critical'}})
            overrides.append({'alias': fields['name'] + ' (c)',
                              'fill': 0, 'legend': False, 'color': '#890F02'})

        if fields['min'] is not None:
            targets.update({'min': {'name': fields['name'] + ' (min)',
                                    'target': my_target + '_min'}})
            overrides.append({'alias': fields['name'] + ' (min)',
                              'fill': 0, 'legend': False, 'color': '#447EBC'})

        if fields['max'] is not None:
            targets.update({'max': {'name': fields['name'] + ' (max)',
                                    'target': my_target + '_max'}})
            overrides.append({'alias': fields['name'] + ' (max)',
                              'fill': 0, 'legend': False, 'color': '#447EBC'})

        alias = True
        if alias:
            for t_name, t_value in iteritems(targets):
                targets[t_name] = "alias(" + t_value['target'] + ", '%s'" % t_value['name'] + ")"

        return targets, overrides

    def create_dashboard(self, host):
        # pylint: disable=too-many-locals
        """
        Create / update a dashboard in Grafana

        :param host: concerned host
        :type host: dict
        :return: True if created, otherwise False
        :rtype: bool
        """
        if not self.datasources:
            return False
        if host['_realm'] not in self.timeseries:
            return False

        self.panel_id = 0

        service_db = current_app.data.driver.db['service']

        # Set host Graphite prefix
        hostname = host['name']
        current_app.logger.info("[grafana-%s] create dashboard for the host '%s'",
                                self.name, hostname)

        # Tags for the targets
        tags = {"host": hostname}
        # Find datasource
        datasource = None
        host_ts_db = self.timeseries[host['_realm']]
        for ds_name, ds_data in iteritems(self.datasources):
            if ds_data['ts_id'] == str(host_ts_db['_id']):
                datasource = ds_name
                break
        if datasource is None:
            current_app.logger.info("----------")
            current_app.logger.info("[grafana-%s] no datasource for the host '%s'",
                                    self.name, hostname)
            current_app.logger.info("----------")
            return False

        rows = []
        targets = []
        # References used by Grafana for each metric in a panel
        refids = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                  'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        perfdata = PerfDatas(host['ls_perf_data'])
        num = 0
        seriesOverrides = []
        for measurement in perfdata.metrics:
            fields = perfdata.metrics[measurement].__dict__
            metrics, overrides = self.build_target(host, fields)
            seriesOverrides.extend(overrides)

            refid = ''
            if num < 26:
                refid = refids[num]

            targets.append(self.generate_target({'measurement': fields['name'],
                                                 'refid': refid,
                                                 'mytarget': metrics['main']},
                                                tags, datasource))

            if fields['warning'] is not None:
                targets.append(self.generate_target({'measurement': fields['name'] + '_warning',
                                                     'refid': refid + '-w',
                                                     'mytarget': metrics['warning']},
                                                    tags, datasource))

            if fields['critical'] is not None:
                targets.append(self.generate_target({'measurement': fields['name'] + '_critical',
                                                     'refid': refid + '-c',
                                                     'mytarget': metrics['critical']},
                                                    tags, datasource))

            if fields['min'] is not None:
                targets.append(self.generate_target({'measurement': fields['name'] + '_min',
                                                     'refid': refid + '-m',
                                                     'mytarget': metrics['min']},
                                                    tags, datasource))

            if fields['max'] is not None:
                targets.append(self.generate_target({'measurement': fields['name'] + '_max',
                                                     'refid': refid + '-M',
                                                     'mytarget': metrics['max']},
                                                    tags, datasource))
            num += 1

        rows.append(self.generate_row("Host %s check alive" % host['name'],
                                      targets, datasource, seriesOverrides))

        # Update host live state
        data = {
            "ls_grafana": True,
            "ls_grafana_panelid": self.panel_id
        }
        lookup = {"_id": host['_id']}
        patch_internal('host', data, False, False, **lookup)

        # now get services
        search = {'host': ObjectId(host['_id']), '_is_template': False,
                  'ls_perf_data': {"$ne": ""}, 'ls_last_check': {"$ne": 0}}
        services = service_db.find(search)
        for service in services:
            service['hostname'] = host['name']
            current_app.logger.info("[grafana-%s] - service: %s", self.name, service['name'])

            # Tags for the service targets
            tags = {"host": hostname, "service": service['name']}

            perfdata = PerfDatas(service['ls_perf_data'])
            targets = []
            seriesOverrides = []
            num = 0
            for measurement in perfdata.metrics:
                fields = perfdata.metrics[measurement].__dict__
                metrics, overrides = self.build_target(service, fields)
                seriesOverrides.extend(overrides)

                refid = ''
                if num < 26:
                    refid = refids[num]

                targets.append(self.generate_target({'measurement': fields['name'],
                                                     'refid': refid,
                                                     'mytarget': metrics['main']},
                                                    tags, datasource))

                if fields['warning'] is not None:
                    targets.append(self.generate_target({'measurement': fields['name'] + '_warning',
                                                         'refid': refid + '-w',
                                                         'mytarget': metrics['warning']},
                                                        tags, datasource))

                if fields['critical'] is not None:
                    targets.append(self.generate_target({'measurement':
                                                         fields['name'] + '_critical',
                                                         'refid': refid + '-c',
                                                         'mytarget': metrics['critical']},
                                                        tags, datasource))

                if fields['min'] is not None:
                    targets.append(self.generate_target({'measurement': fields['name'] + '_min',
                                                         'refid': refid + '-m',
                                                         'mytarget': metrics['min']},
                                                        tags, datasource))

                if fields['max'] is not None:
                    targets.append(self.generate_target({'measurement': fields['name'] + '_max',
                                                         'refid': refid + '-M',
                                                         'mytarget': metrics['max']},
                                                        tags, datasource))

                num += 1

            rows.append(self.generate_row(service['name'], targets, datasource, seriesOverrides))

            # Update service live state
            data = {
                "ls_grafana": True,
                "ls_grafana_panelid": self.panel_id
            }
            lookup = {"_id": service['_id']}
            patch_internal('service', data, False, False, **lookup)

        # Find the TS corresponding to the host realm
        ts = self.timeseries[host['_realm']]

        headers = {"Authorization": "Bearer " + self.api_key}
        data = {
            "dashboard": {
                'id': None,
                'title': "Host: " + hostname,
                'tags': ['alignak', 'host'],
                'style': 'dark',
                'timezone': self.dashboard_data['timezone'],
                'refresh': self.dashboard_data['refresh'],
                'editable': True,
                'hideControls': False,
                'graphTooltip': 1,
                'rows': rows,
                'time': {
                    'from': 'now-6h',
                    'to': 'now'
                },
                'timepicker': {
                    'time_options': [
                        '30m', '1h', '6h', '12h', '24h', '2d', '7d', '30d'
                    ],
                    'refresh_intervals': [
                        '5s', '10s', '30s', '1m', '5m', '15m', '30m', '1h', '2h'
                    ]
                },
                'templating': {
                    'list': [
                        {
                            'allValue': None,
                            'current': {
                                'text': ts['ts_prefix'],
                                'value': ts['ts_prefix']
                            },
                            'hide': 0 if ts['ts_prefix'] != '' else 1,
                            'includeAll': False,
                            'label': 'Time series prefix',
                            'multi': False,
                            'name': 'ts_prefix',
                            'options': [
                                {
                                    'text': ts['ts_prefix'],
                                    'value': ts['ts_prefix'],
                                    'selected': True
                                }
                            ],
                            'query': ts['ts_prefix'],
                            'type': 'custom',
                            'datasource': None,
                            'allFormat': 'glob'
                        },
                        {
                            'allValue': None,
                            'current': {
                                'text': ts['statsd_prefix'],
                                'value': ts['statsd_prefix']
                            },
                            'hide': 0 if ts['statsd_prefix'] != '' else 1,
                            'includeAll': False,
                            'label': 'StatsD prefix',
                            'multi': False,
                            'name': 'statsd_prefix',
                            'options': [
                                {
                                    'text': ts['statsd_prefix'],
                                    'value': ts['statsd_prefix'],
                                    'selected': True
                                }
                            ],
                            'query': ts['statsd_prefix'],
                            'type': 'custom',
                            'datasource': None,
                            'allFormat': 'glob'
                        }
                    ]
                },
                'annotations': {
                    'list': []
                },
                "schemaVersion": 7,
                "version": 0,
                "links": []
            },
            "overwrite": True
        }
        try:
            requests.post(self.scheme + '://' + self.host + ':' + self.port + '/api/dashboards/db',
                          json=data, headers=headers, timeout=10)
            return True
        except requests.exceptions.SSLError as e:
            print("[cron_grafana] SSL connection error to grafana %s for dashboard creation: %s" %
                  (self.name, e))
            current_app.logger.error("[cron_grafana] SSL connection error to grafana %s "
                                     "for dashboard creation: %s", self.name, e)
            return False
        except requests.exceptions.RequestException as e:
            print("[cron_grafana] Connection error to grafana %s for dashboard creation: %s" %
                  (self.name, e))
            current_app.logger.error("[cron_grafana] Connection error to grafana %s "
                                     "for dashboard creation: %s", self.name, e)
            return False

    def get_datasources(self):
        """
        Get datasource or create it if it does not exist

        :return: None
        """
        headers = {"Authorization": "Bearer " + self.api_key}
        try:
            url = "%s://%s:%s/api/datasources" % (self.scheme, self.host, self.port)
            response = requests.get(url, headers=headers, timeout=10)
        except requests.exceptions.SSLError as e:
            print("[cron_grafana] SSL connection error to grafana %s: %s" % (self.name, e))
            current_app.logger.error("[cron_grafana] SSL connection error to grafana %s "
                                     "for dashboard creation: %s", self.name, e)
            return
        except requests.exceptions.RequestException as e:
            print("[cron_grafana] Connection error to grafana %s: %s" % (self.name, e))
            current_app.logger.error("[cron_grafana] Connection error to grafana %s "
                                     "for dashboard creation: %s", self.name, e)
            self.connection = False
            return
        resp = response.json()
        if 'message' in resp:
            print("----------")
            print("Grafana message: %s" % resp['message'])
            print("----------")
            return

        # get existing datasource in grafana
        self.datasources = {}
        for datasource in iter(resp):
            self.datasources[datasource['name']] = {'id': datasource['id'], 'ts_id': None}

        # associate the datasource to timeseries data
        for _, timeserie in iteritems(self.timeseries):
            ds_name = 'alignak-' + timeserie['type'] + '-' + timeserie['name']
            if ds_name in self.datasources.keys():
                self.datasources[ds_name]['ts_id'] = str(timeserie['_id'])
                continue

            # Missing datasource, create it
            # Note that no created datasource is the default one
            if timeserie['type'] == 'influxdb':
                data = {
                    "name": ds_name,
                    "type": "influxdb",
                    "typeLogoUrl": "",
                    "access": "proxy",
                    "url": "http://" + timeserie['address'] + ":" + str(timeserie['port']),
                    "password": timeserie['password'],
                    "user": timeserie['login'],
                    "database": timeserie['database'],
                    "basicAuth": False,
                    "basicAuthUser": "",
                    "basicAuthPassword": "",
                    "withCredentials": False,
                    "isDefault": False,
                    "jsonData": {}
                }
            elif timeserie['type'] == 'graphite':
                data = {
                    "name": ds_name,
                    "type": "graphite",
                    "access": "proxy",
                    "url": "http://%s:%s" % (timeserie['graphite_address'],
                                             timeserie['graphite_port']),
                    "basicAuth": False,
                    "basicAuthUser": "",
                    "basicAuthPassword": "",
                    "withCredentials": False,
                    "isDefault": False,
                    "jsonData": {}
                }

            # Request datasource creation
            response = requests.post(
                self.scheme + '://' + self.host + ':' + self.port + '/api/datasources',
                json=data, headers=headers)
            resp = response.json()
            # resp is as: {u'message': u'Datasource added', u'id': 4}
            if 'id' not in resp and 'message' in resp:
                current_app.logger.info("Grafana message: %s", resp['message'])
                return
            current_app.logger.info("[grafana-%s] datasource created: '%s': id = %s",
                                    self.name, ds_name, resp['id'])
            self.datasources[ds_name] = {'id': resp['id'], 'ts_id': str(timeserie['_id'])}

        current_app.logger.info("[grafana-%s] available datasources:", self.name)
        for ds_name, datasource in iteritems(self.datasources):
            current_app.logger.info("- %s: %s", ds_name, datasource)

    @staticmethod
    def generate_target(elements, tags, datasource):
        # measurement, refid, mytarget):
        """
        Generate target structure for dashboard

        :param elements: dictionary with elements: measurement, refid, mytarget
        :type elements: dict
        :param tags: list of tags
        :type tags: dict
        :param datasource: datasource name
        :type datasource: str
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
            if prepare_tags:
                data['condition'] = 'AND'
            prepare_tags.append(data)

        return {
            "dsType": datasource,
            "measurement": elements['measurement'],
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
            "target": elements['mytarget'],
            "refId": elements['refid'],
        }

    def generate_row(self, title, targets, datasource, seriesOverrides):
        """
        Generate a row in dashboard

        :param title: Name of the row / graph
        :type title: str
        :param targets: all targets (all measurements in the row/graph)
        :type targets: list
        :param datasource: datasource name
        :type datasource: str
        :param seriesOverrides: List of aliases for display
        :type seriesOverrides: list
        :return: the dictionary of the row
        :rtype: dict
        """
        self.panel_id += 1
        return {
            "collapse": False,
            "editable": True,
            "title": title,
            "height": "250px",
            "panels": [
                {
                    "title": title,
                    "error": False,
                    "span": 12,
                    "editable": True,
                    "datasource": datasource,
                    "type": "graph",
                    "id": self.panel_id,
                    "targets": targets,
                    "lines": True,
                    "fill": 1,
                    "linewidth": 2,
                    "points": False,
                    "pointradius": 5,
                    "bars": False,
                    "stack": False,
                    "percentage": False,
                    "legend": {
                        "avg": True,
                        "current": True,
                        "max": True,
                        "min": True,
                        "show": True,
                        "total": False,
                        "values": True,
                        "alignAsTable": True
                    },
                    "nullPointMode": "connected",
                    "steppedLine": False,
                    "tooltip": {
                        "value_type": "cumulative",
                        "shared": True,
                        "sort": 0,
                        "msResolution": False
                    },
                    "timeFrom": None,
                    "timeShift": None,
                    "aliasColors": {},
                    "seriesOverrides": seriesOverrides,
                    "thresholds": [],
                    "links": []
                }
            ]
        }
