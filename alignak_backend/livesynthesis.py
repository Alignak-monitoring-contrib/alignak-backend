#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.livesynthesis`` module

    This module manages the livesynthesis
"""
from __future__ import print_function
from flask import current_app, g, request, abort, jsonify
from eve.methods.patch import patch_internal


class Livesynthesis(object):
    """
        Livesynthesis class
    """
    @staticmethod
    def recalculate():
        """
            Recalculate all the live synthesis counters
        """
        livesynthesis = current_app.data.driver.db['livesynthesis']
        live_current = livesynthesis.find_one()
        if live_current is None:
            data = {
                'hosts_total': 0,
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
        hosts = current_app.data.driver.db['host']
        hosts_cnt = hosts.find({'_is_template': False}).count()
        livestates = current_app.data.driver.db['livestate']
        if live_current['hosts_total'] != hosts_cnt:
            data = {"hosts_total": hosts_cnt}
            data['hosts_up_hard'] = livestates.find(
                {"service_description": None, "state": "UP"}).count()
            data['hosts_down_hard'] = livestates.find(
                {"service_description": None, "state": "DOWN"}).count()
            data['hosts_unreachable_hard'] = livestates.find(
                {"service_description": None, "state": "UNREACHABLE"}).count()
            lookup = {"_id": live_current['_id']}
            patch_internal('livesynthesis', data, False, False, **lookup)

        # get all services
        services = current_app.data.driver.db['service']
        services_cnt = services.find({'_is_template': False}).count()
        if live_current['services_total'] != services_cnt:
            data = {"services_total": services_cnt}
            data['services_ok_hard'] = livestates.find({"state": "OK"}).count()
            data['services_warning_hard'] = livestates.find({"state": "WARNING"}).count()
            data['services_critical_hard'] = livestates.find({"state": "CRITICAL"}).count()
            data['services_unknown_hard'] = livestates.find({"state": "UNKNOWN"}).count()
            lookup = {"_id": live_current['_id']}
            patch_internal('livesynthesis', data, False, False, **lookup)

    @staticmethod
    def on_updated_livestate(updated, original):
        """
            What to do when the livestate is updated ...
        """
        minus, plus = Livesynthesis.livesynthesis_to_update(updated, original)
        if minus:
            livesynthesis_db = current_app.data.driver.db['livesynthesis']
            live_current = livesynthesis_db.find_one()
            if live_current is None:
                ls = Livesynthesis()
                ls.recalculate()
            data = {"$inc": {minus: -1, plus: 1}}
            current_app.data.driver.db.livesynthesis.update({'_id': live_current['_id']}, data)

    @staticmethod
    def livesynthesis_to_update(updated, original):
        """
        Define fields counters to minus and plus (or nothing to do)

        :param updated:
        :param original:
        :return: list with field name (minus, plus)
        :rtype: list
        """
        type_check = 'services'
        if original['service_description'] is None:
            type_check = 'hosts'
        if 'state' not in updated and 'state_type' not in updated:
            return False, False
        elif 'state' in updated and 'state_type' not in updated:
            plus = "%s_%s_%s" % (type_check, updated['state'].lower(),
                                 original['state_type'].lower())
        elif 'state' not in updated and 'state_type' in updated:
            plus = "%s_%s_%s" % (type_check, original['state'].lower(),
                                 updated['state_type'].lower())
        else:
            # so have 'state' and 'state_type' in updated
            plus = "%s_%s_%s" % (type_check, updated['state'].lower(),
                                 updated['state_type'].lower())
        minus = "%s_%s_%s" % (type_check, original['state'].lower(),
                              original['state_type'].lower())
        if minus == plus:
            return False, False
        return minus, plus

    @staticmethod
    def on_inserted_livestate(items):
        """
            What to do when an element is inserted in the livestate ...
        """
        livesynthesis_db = current_app.data.driver.db['livesynthesis']
        live_current = livesynthesis_db.find_one()
        if live_current is None:
            ls = Livesynthesis()
            ls.recalculate()
        else:
            for dummy, item in enumerate(items):
                typecheck = 'services'
                if item['service_description'] is None:
                    typecheck = 'hosts'
                data = {"$inc": {"%s_%s_%s" % (typecheck, item['state'].lower(),
                                               item['state_type'].lower()): 1,
                                 "%s_total" % (typecheck): 1}}
                current_app.data.driver.db.livesynthesis.update({'_id': live_current['_id']}, data)
