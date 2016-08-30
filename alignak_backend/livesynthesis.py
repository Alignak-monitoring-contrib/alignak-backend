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
        realmsdrv = current_app.data.driver.db['realm']
        allrealms = realmsdrv.find()
        for _, realm in enumerate(allrealms):
            live_current = livesynthesis.find_one({'_realm': realm['_id']})
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
                    'services_business_impact': 0,
                    '_realm': realm['_id']
                }
                livesynthesis.insert(data)
                live_current = livesynthesis.find_one({'_realm': realm['_id']})

            # Update hosts live synthesis
            hosts = current_app.data.driver.db['host']
            hosts_count = hosts.find({'_is_template': False, '_realm': realm['_id']}).count()
            if live_current['hosts_total'] != hosts_count:
                data = {"hosts_total": hosts_count}

                data['hosts_up_hard'] = hosts.find({
                    "ls_state": "UP", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['hosts_down_hard'] = hosts.find({
                    "ls_state": "DOWN", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['hosts_unreachable_hard'] = hosts.find({
                    "ls_state": "UNREACHABLE", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()

                data['hosts_up_soft'] = hosts.find({
                    "ls_state": "UP", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['hosts_down_soft'] = hosts.find({
                    "ls_state": "DOWN", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['hosts_unreachable_soft'] = hosts.find({
                    "ls_state": "UNREACHABLE", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()

                data['hosts_acknowledged'] = hosts.find(
                    {'ls_acknowledged': True, "_realm": realm["_id"]}
                ).count()
                data['hosts_in_downtime'] = hosts.find(
                    {'ls_downtimed': True, "_realm": realm["_id"]}
                ).count()

                lookup = {"_id": live_current['_id']}
                patch_internal('livesynthesis', data, False, False, **lookup)

            # Update services live synthesis
            services = current_app.data.driver.db['service']
            services_count = services.find({'_is_template': False, '_realm': realm['_id']}).count()
            if live_current['services_total'] != services_count:
                data = {"services_total": services_count}

                data['services_ok_hard'] = services.find({
                    "ls_state": "OK", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_warning_hard'] = services.find({
                    "ls_state": "WARNING", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_critical_hard'] = services.find({
                    "ls_state": "CRITICAL", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_unknown_hard'] = services.find({
                    "ls_state": "UNKNOWN", "ls_state_type": "HARD",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()

                data['services_ok_soft'] = services.find({
                    "ls_state": "OK", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_warning_soft'] = services.find({
                    "ls_state": "WARNING", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_critical_soft'] = services.find({
                    "ls_state": "CRITICAL", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()
                data['services_unknown_soft'] = services.find({
                    "ls_state": "UNKNOWN", "ls_state_type": "SOFT",
                    "ls_acknowledged": False, "_realm": realm["_id"]
                }).count()

                data['services_acknowledged'] = services.find(
                    {"ls_acknowledged": True, "_realm": realm["_id"]}
                ).count()
                data['services_in_downtime'] = services.find(
                    {"downtimed": True, "_realm": realm["_id"]}
                ).count()
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
        if original['service'] is None:
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

        # check acknowledge
        if 'acknowledged' in updated and updated['acknowledged'] and not original['acknowledged']:
            plus = "%s_acknowledged" % (type_check)
        elif 'acknowledged' in updated and not updated['acknowledged'] \
                and original['acknowledged']:
            minus = "%s_acknowledged" % (type_check)
        elif 'acknowledged' in original and original['acknowledged']:
            return False, False

        if minus == plus:
            return False, False
        return minus, plus

    @staticmethod
    def on_inserted_livestate(items):
        """
            What to do when an element is inserted in the livestate ...
        """
        livesynthesis_db = current_app.data.driver.db['livesynthesis']
        for _, item in enumerate(items):
            live_current = livesynthesis_db.find_one({'_realm': item['_realm']})
            if live_current is None:
                ls = Livesynthesis()
                ls.recalculate()
            else:
                typecheck = 'services'
                if item['service'] is None:
                    typecheck = 'hosts'
                data = {"$inc": {"%s_%s_%s" % (typecheck, item['state'].lower(),
                                               item['state_type'].lower()): 1,
                                 "%s_total" % (typecheck): 1}}
                current_app.data.driver.db.livesynthesis.update({'_id': live_current['_id']}, data)
