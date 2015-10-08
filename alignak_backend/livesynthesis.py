#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.livesynthesis`` module

    This module manages the livesynthesis
"""
from __future__ import print_function
from flask import current_app, g, request, abort, jsonify


class Livesynthesis(object):

    def __init__(self, app):
        self.app = app

    def recalculate(self):
        livesynthesis = self.app.data.driver.db['livesynthesis']
        live_current = livesynthesis.find_one()
        if live_current is None:
            data = {'hosts_total': 0,
                    'hosts_up_hard': 0,
                    'hosts_up_soft': 0,
                    'hosts_down_hard': 0,
                    'hosts_down_soft': 0,
                    'hosts_unreachable_hard': 0,
                    'hosts_unreachable_soft': 0,
                    'hosts_acknowledged': 0,
                    'hosts_in_downtime': 0,
                    'hosts_flapping': 0,
                    'hosts_business_impact': 0,
                    'services_total': 0,
                    'services_ok_hard': 0,
                    'services_ok_soft': 0,
                    'services_warning_hard': 0,
                    'services_warning_soft': 0,
                    'services_critical_hard': 0,
                    'services_critical_soft': 0,
                    'services_unknown_hard': 0,
                    'services_unknown_soft': 0,
                    'services_acknowledged': 0,
                    'services_in_downtime': 0,
                    'services_flapping': 0,
                    'services_business_impact': 0
                    }
            livesynthesis.insert(data)
            live_current = livesynthesis.find_one()
        # get all hosts
        hosts = self.app.data.driver.db['host']
        hosts_cnt = hosts.find({"register": True}).count()
        livestates = self.app.data.driver.db['livestate']
        if live_current['hosts_total'] != hosts_cnt:
            data = {"hosts_total": hosts_cnt}
            data['hosts_up_hard'] = livestates.find(
                {"service_description": None, "state": "UP"}).count()
            data['hosts_down_hard'] = livestates.find(
                {"service_description": None, "state": "DOWN"}).count()
            data['hosts_unreachable_hard'] = livestates.find(
                {"service_description": None, "state": "UNREACHABLE"}).count()
            self.app.data.update('livesynthesis', live_current['_id'], data)

        # get all services
        services = self.app.data.driver.db['service']
        services_cnt = services.find({"register": True}).count()
        if live_current['services_total'] != services_cnt:
            data = {"services_total": services_cnt}
            data['services_ok_hard'] = livestates.find(
                {"service_description": "{$not: [null]}", "state": "OK"}).count()
            data['services_warning_hard'] = livestates.find(
                {"service_description": "{$not: [null]}", "state": "WARNING"}).count()
            data['services_critical_hard'] = livestates.find(
                {"service_description": "{$not: [null]}", "state": "CRITICAL"}).count()
            data['services_unknown_hard'] = livestates.find(
                {"service_description": "{$not: [null]}", "state": "UNKNOWN"}).count()
            self.app.data.update('livesynthesis', live_current['_id'], data)

    @staticmethod
    def on_updated_livestate(updated, original):
        if updated['state'] == updated['last_state'] \
                and updated['state_type'] == updated['last_state_type']:
            return

        livesynthesis = current_app.data.driver.db['livesynthesis']
        live_current = livesynthesis.find_one()
        typecheck = 'services'
        if original['service_description'] is None:
            typecheck = 'hosts'
        data = {"$inc": {"%s_%s_%s" % (typecheck, updated['last_state'].lower(),
                                       updated['last_state_type'].lower()): -1,
                         "%s_%s_%s" % (typecheck, updated['state'].lower(),
                                       updated['state_type'].lower()): 1}}
        current_app.data.driver.db.livesynthesis.update({'_id': live_current['_id']}, data)

    @staticmethod
    def on_inserted_livestate(items):
        livesynthesis = current_app.data.driver.db['livesynthesis']
        live_current = livesynthesis.find_one()
        for index, item in enumerate(items):
            typecheck = 'services'
            if item['service_description'] is None:
                typecheck = 'hosts'
            data = {"$inc": {"%s_%s_%s" % (typecheck, item['state'].lower(),
                                           item['state_type'].lower()): 1}}
            current_app.data.driver.db.livesynthesis.update({'_id': live_current['_id']}, data)
