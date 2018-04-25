#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.timeseries`` module

    This module manages the timeseries carbon / influxdb
"""
from __future__ import print_function
import os
import re
import time
from flask import current_app
from influxdb import InfluxDBClient
import statsd

from eve.methods.post import post_internal
from alignak_backend.carboniface import CarbonIface
from alignak_backend.perfdata import PerfDatas, Metric


class Timeseries(object):
    """
        Timeseries class
    """

    @staticmethod
    def sanitize_name(field_name):
        """Sanitize a field name for aTSDB (Graphite or Influx)
        - remove unallowed characters from the field name

        :param field_name: Field name to clean
        :type field_name: string
        :return: sanitized field name
        """

        # Sanitize field name for TSDB (Graphite or Influx):
        sanitized = field_name.strip()
        if sanitized.startswith('/'):
            sanitized = '_' + sanitized[1:]
        # + becomes a _
        sanitized = sanitized.replace("+", "_")
        # / becomes a -
        sanitized = sanitized.replace("/", "-")
        # space becomes a _
        sanitized = sanitized.replace(" ", "_")
        # % becomes _pct
        sanitized = sanitized.replace("%", "_pct")
        # all character not in [a-zA-Z_-0-9.] is removed
        sanitized = re.sub(r'[^a-zA-Z_\-0-9\.\$]', '', sanitized)

        return sanitized

    @staticmethod
    def send_livesynthesis_metrics(realm_uuid, livesynthesis):
        """Called to send the livesynthesis metrics to the configured TSDB

        :param items: List of logcheckresult inserted
        :type items: list
        :return: None
        """
        ls = {'perf_data': []}
        for counter in livesynthesis:
            if counter.startswith('_'):
                continue
            current_app.logger.debug("   - counter: %s", counter)
            ls['perf_data'].append("%s=%d" % (counter, livesynthesis[counter]))

        ls['perf_data'] = " ".join(ls['perf_data'])
        current_app.logger.debug("   - perf_data: %s", ls['perf_data'])

        ts = Timeseries.prepare_data(ls)
        send_data = []
        for d in ts['data']:
            send_data.append({
                "realm": Timeseries.get_realms_prefix(realm_uuid),
                "host": 'alignak_livesynthesis',
                "service": '',
                "timestamp": int(time.time()),
                "name": d['name'],
                # Cast as a string to bypass int/float real value
                "value": str(d['value']),
                "uom": d['uom']
            })
        Timeseries.send_to_timeseries_db(send_data, realm_uuid)

    @staticmethod
    def after_inserted_logcheckresult(items):
        """Called by EVE HOOK (app.on_inserted_logcheckresult)

        :param items: List of logcheckresult inserted
        :type items: list
        :return: None
        """
        host_db = current_app.data.driver.db['host']
        service_db = current_app.data.driver.db['service']
        for dummy, item in enumerate(items):
            host_info = host_db.find_one({'_id': item['host']})
            if not host_info['process_perf_data']:
                continue
            item_realm = host_info['_realm']
            item['_overall_state_id'] = host_info['_overall_state_id']
            host_name = Timeseries.sanitize_name(host_info['name'])
            service_name = ''
            if item['service'] is not None:
                service_info = service_db.find_one({'_id': item['service']})
                if not service_info['process_perf_data']:
                    continue
                service_name = Timeseries.sanitize_name(service_info['name'])
                # todo: really? a service realm may be different from its host's realm ?
                item_realm = service_info['_realm']
                item['_overall_state_id'] = service_info['_overall_state_id']
            ts = Timeseries.prepare_data(item)
            send_data = []
            for d in ts['data']:
                send_data.append({
                    # todo: sure not to use item_realm?
                    "realm": Timeseries.get_realms_prefix(item['_realm']),
                    "host": host_name,
                    "service": service_name,
                    "name": d['name'],
                    # Cast as a string to bypass int/float real value
                    "value": str(d['value']),
                    "timestamp": item['last_check'],
                    "uom": d['uom']
                })
            Timeseries.send_to_timeseries_db(send_data, item_realm)

    @staticmethod
    def prepare_data(item):
        """Split and prepare perfdata to after send to timeseries database

        :param item: fields added in mongo (logcheckresult)
        :type item: dict
        :return:
        """
        data_timeseries = {
            'data': [],
        }

        perfdata = PerfDatas(item['perf_data'])

        # Add a metric for the item state (host, service)
        if 'state_id' in item:
            metric = Metric("alignak_state_id=%s" % item['state_id'])
            if metric.name is not None:
                perfdata.metrics[metric.name] = metric

        # Add a metric for an item overall state (host, service)
        if '_overall_state_id' in item:
            if item['_overall_state_id'] == 5:
                item['_overall_state_id'] = -1
            metric = Metric("alignak_overall_state_id=%s" % item['_overall_state_id'])
            if metric.name is not None:
                perfdata.metrics[metric.name] = metric

        for measurement in perfdata.metrics:
            fields = perfdata.metrics[measurement].__dict__
            # case we have .timestamp in the name
            m = re.search(r'^(.*)\.[\d]{10}$', fields['name'])
            if m:
                fields['name'] = m.group(1)

            # Sanitize field name for TSDB (Graphite or Influx):
            fields['name'] = Timeseries.sanitize_name(fields['name'])

            if fields['value'] is not None:
                data_timeseries['data'].append(
                    {
                        'name': fields['name'],
                        'value': fields['value'],
                        'uom': fields['uom']
                    }
                )
            if fields['warning'] is not None:
                data_timeseries['data'].append(
                    {
                        'name': fields['name'] + '_warning',
                        'value': fields['warning'],
                        'uom': fields['uom']
                    }
                )
            if fields['critical'] is not None:
                data_timeseries['data'].append(
                    {
                        'name': fields['name'] + '_critical',
                        'value': fields['critical'],
                        'uom': fields['uom']
                    }
                )
            if fields['min'] is not None:
                data_timeseries['data'].append(
                    {
                        'name': fields['name'] + '_min',
                        'value': fields['min'],
                        'uom': fields['uom']
                    }
                )
            if fields['max'] is not None:
                data_timeseries['data'].append(
                    {
                        'name': fields['name'] + '_max',
                        'value': fields['max'],
                        'uom': fields['uom']
                    }
                )
        return data_timeseries

    @staticmethod
    def get_realms_prefix(realm_id):
        """Get realms path from top level

        :param realm_id: id of the realm
        :type realm_id: str
        :return: realms name separed by .
        :rtype: str
        """
        prefix_realm = ''
        realm_db = current_app.data.driver.db['realm']
        realm_info = realm_db.find_one({'_id': realm_id})
        if realm_info['_tree_parents']:
            realms = realm_db.find({'_id': {"$in": realm_info['_tree_parents']}}).sort("_level")
            for realm in realms:
                prefix_realm += realm['name'] + "."
        prefix_realm += realm_info['name']
        return prefix_realm

    @staticmethod
    def send_to_timeseries_db(data, item_realm):
        """Send perfdata to timeseries databases.

        If TSDB is not available, store the perf_data in the internal retention store

        `data` must have this structure:
        [
            {
                "name": "",
                "realm"; "",
                "host": "",
                "service": "",
                "value": 000,
                "timestamp": 000
                "uom": ""
            }
        ]

        :param data: Information of data to send to carbon / influxdb
        :type data: list
        :param item_realm: id of the realm
        :type item_realm: str
        :return: None
        """
        graphite_db = current_app.data.driver.db['graphite']
        influxdb_db = current_app.data.driver.db['influxdb']
        realm_db = current_app.data.driver.db['realm']

        searches = [{'_realm': item_realm}]
        realm_info = realm_db.find_one({'_id': item_realm})
        for realm in realm_info['_tree_parents']:
            searches.append({'_realm': realm, '_sub_realm': True})

        # get graphite servers to send to
        for search in searches:
            graphites = graphite_db.find(search)
            for graphite in graphites:
                if not Timeseries.send_to_timeseries_graphite(data, graphite):
                    for perf in data:
                        perf['graphite'] = graphite['_id']
                    post_internal('timeseriesretention', data)
                    for perf in data:
                        del perf['graphite']

        # get influxdb servers to send to
        for search in searches:
            influxdbs = influxdb_db.find(search)
            for influxdb in influxdbs:
                if not Timeseries.send_to_timeseries_influxdb(data, influxdb):
                    for perf in data:
                        perf['influxdb'] = influxdb['_id']
                    post_internal('timeseriesretention', data)
                    for perf in data:
                        del perf['influxdb']

    @staticmethod
    def send_to_timeseries_graphite(data, graphite):
        """Send perfdata to graphite/carbon timeseries database

        :param data: list of perfdata to send to graphite / carbon
        :type data: list
        :param graphite: graphite properties dictionary
        :type graphite: dict
        :return: True if successful or not have graphite configured, otherwise False
        :rtype: bool
        """
        if graphite['statsd'] is not None:
            return Timeseries.send_to_statsd(data, graphite['statsd'], graphite['prefix'])

        send_data = []
        for d in data:
            if d['service'] == '':
                prefix = d['host']
            else:
                prefix = '.'.join([d['host'], d['service']])
            # manage realms prefix of graphite server
            if graphite.get('realms_prefix'):
                prefix = d['realm'] + '.' + prefix
            # manage prefix of graphite server
            if graphite['prefix'] != '':
                prefix = graphite['prefix'] + '.' + prefix
            current_app.logger.debug("[tsdb] data: %s", ('.'.join([prefix, d['name']]),
                                                         (int(d['timestamp']), d['value'])))
            send_data.append(('.'.join([prefix, d['name']]),
                              (int(d['timestamp']), d['value'])))
        carbon = CarbonIface(graphite['carbon_address'], graphite['carbon_port'])
        try:
            current_app.logger.debug("[tsdb] sending %d data to Graphite (%s:%s)...",
                                     len(send_data),
                                     graphite['carbon_address'], graphite['carbon_port'])
            carbon.send_data(send_data)
            return True
        except Exception as exp:
            current_app.logger.warning("Failed sending metrics to Graphite, exception: %s",
                                       str(exp))
            return False

    @staticmethod
    def send_to_timeseries_influxdb(data, influxdb):
        """Send perfdata to influxdb timeseries database

        :param data: list of perfdata to send to influxdb
        :type data: list
        :param influxdb: influxdb properties dictionary
        :type influxdb: dict
        :return: True if successful or not have influxdb configured, otherwise False
        :rtype: bool
        """
        if influxdb['statsd'] is not None:
            return Timeseries.send_to_statsd(data, influxdb['statsd'], '')

        json_body = []
        for d in data:
            json_body.append({
                "measurement": str(d['name']),
                "tags": {
                    "host": d['host'],
                    "service": d['service'],
                    "realm": '.'.join(d['realm'])
                },
                "time": d['timestamp'] * 1000000000,
                "fields": {
                    "value": float(d['value'])
                }
            })
        influxdbs = InfluxDBClient(influxdb['address'], influxdb['port'], influxdb['login'],
                                   influxdb['password'], influxdb['database'], timeout=1)
        try:
            influxdbs.write_points(json_body)
            return True
        except:  # pylint: disable=W0702
            return False

    @staticmethod
    def send_to_statsd(data, statsd_id, prefix):
        """Send data to statsd

        Do not take care of the StatsD prefix because it is managed internally by the
        StatsD daemon

        Provide the Graphite prefix to the StatsD client

        :param data: list of perfdata to send to statsd
        :type data: list
        :param statsd_id: id of statsd
        :type statsd_id: str
        :param prefix: prefix string used for each value name
        :type prefix: str
        :return: True (because statsd not have return error or not)
        :rtype: bool
        """
        statsd_db = current_app.data.driver.db['statsd']
        item = statsd_db.find_one({'_id': statsd_id})
        statsd_instance = statsd.StatsClient(item['address'], item['port'], prefix=prefix)
        for d in data:
            if d['service'] == '':
                prefix = '.'.join([d['realm'], d['host']])
            else:
                prefix = '.'.join([d['realm'], d['host'], d['service']])

            if d["uom"] in ['s', 'ms']:
                statsd_instance.timing('.'.join([prefix, d['name']]), float(d['value']))
            elif d["uom"] == 'h':
                statsd_instance.incr('.'.join([prefix, d['name']]), int(d['value']))
            else:
                statsd_instance.gauge('.'.join([prefix, d['name']]), float(d['value']))
        return True
