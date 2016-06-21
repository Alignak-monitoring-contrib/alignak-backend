#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.livestate`` module

    This module manages the livestate
"""
from __future__ import print_function
from flask import current_app, g, request, abort, jsonify
from eve.methods.post import post_internal
from eve.methods.patch import patch_internal


class Livestate(object):
    """
        Livestate class
    """

    @staticmethod
    def recalculate():
        """
            Recalculate all the live state
        """
        livestate = current_app.data.driver.db['livestate']
        if livestate.count() == 0:
            host = current_app.data.driver.db['host']
            hosts = host.find({'_is_template': False})
            for h in hosts:
                Livestate.on_inserted_host([h])
            service = current_app.data.driver.db['service']
            services = service.find({'_is_template': False})
            for s in services:
                Livestate.on_inserted_service([s])

    @staticmethod
    def on_inserted_host(items):
        """
            What to do when a new host is inserted in the live state ...
        """
        for dummy, item in enumerate(items):
            if item['_is_template']:
                continue
            name = ''
            if 'display_name' in item and item['display_name'] != '':
                name = item['display_name']
            elif 'alias' in item and item['alias'] != '':
                name = item['alias']
            else:
                name = item['name']

            data = {'host': item['_id'], 'service': None, 'state': 'UP',
                    'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'UP', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': '', 'type': 'host',
                    'business_impact': item['business_impact'], 'display_name_host': name,
                    '_realm': item['_realm'], 'name': item['name']}
            if item['initial_state'] == 'd':
                data['state'] = 'DOWN'
                data['state_id'] = 1
                data['last_state'] = 'DOWN'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNREACHABLE'
                data['state_id'] = 2
                data['last_state'] = 'UNREACHABLE'
            post_internal("livestate", data)

    @staticmethod
    def on_inserted_service(items):
        """
            What to do when a new service is inserted in the live state ...
        """
        for dummy, item in enumerate(items):
            if item['_is_template']:
                continue
            name = ''
            if 'display_name' in item and item['display_name'] != '':
                name = item['display_name']
            elif 'alias' in item and item['alias'] != '':
                name = item['alias']
            else:
                name = item['name']

            host_db = current_app.data.driver.db['host']
            host_info = host_db.find_one({'_id': item['host']})
            if not host_info:
                print("Host not found: %s" % item)
                return
            name_h = host_info['name']
            if 'alias' in host_info and host_info['alias'] != '':
                name_h = host_info['alias']
            if 'display_name' in host_info and host_info['display_name'] != '':
                name_h = host_info['display_name']

            data = {'host': item['host'], 'service': item['_id'],
                    'state': 'OK', 'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'OK', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': '', 'type': 'service',
                    'business_impact': item['business_impact'], 'display_name_service': name,
                    'display_name_host': name_h, '_realm': item['_realm'],
                    'name': host_info['name'] + '/' + item['name']}
            if item['initial_state'] == 'w':
                data['state'] = 'WARNING'
                data['state_id'] = 1
                data['last_state'] = 'WARNING'
            elif item['initial_state'] == 'c':
                data['state'] = 'CRITICAL'
                data['state_id'] = 2
                data['last_state'] = 'CRITICAL'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNKNOWN'
                data['state_id'] = 3
                data['last_state'] = 'UNKNOWN'
            post_internal("livestate", data)

    @staticmethod
    def on_updated_host(updated, original):
        """
            Update field business_impact if changed
        """
        if original['_is_template']:
            return
        bi = True
        if 'business_impact' not in updated:
            bi = False
        elif updated['business_impact'] == original['business_impact']:
            bi = False

        name = ''
        if 'display_name' in updated and updated['display_name'] != '':
            name = updated['display_name']
        elif 'display_name' in original and original['display_name'] != '':
            name = ''
        elif 'alias' in updated and updated['alias'] != '':
            name = updated['alias']
        elif 'alias' in original and original['alias'] != '':
            name = ''
        elif 'name' in updated and updated['name'] != '':
            name = updated['name']

        if bi or name != '':
            livestate_db = current_app.data.driver.db['livestate']
            live_current = livestate_db.find_one({'host': original['_id'],
                                                  'service': None})
            data = {}
            if bi:
                data['business_impact'] = updated['business_impact']
            if name != '':
                data['display_name_host'] = name
            lookup = {"_id": live_current['_id']}
            patch_internal('livestate', data, False, False, **lookup)
            if name != '':
                lives = livestate_db.find({'host': original['_id'], 'type': 'service'})
                data = {'display_name_host': name}
                for live in lives:
                    lookup = {"_id": live['_id']}
                    patch_internal('livestate', data, False, False, **lookup)

    @staticmethod
    def on_updated_service(updated, original):
        """
            Update field business_impact if changed
        """
        if original['_is_template']:
            return
        bi = True
        if 'business_impact' not in updated:
            bi = False
        elif updated['business_impact'] == original['business_impact']:
            bi = False

        name = ''
        if 'display_name' in updated and updated['display_name'] != '':
            name = updated['display_name']
        elif 'display_name' in original and original['display_name'] != '':
            name = ''
        elif 'alias' in updated and updated['alias'] != '':
            name = updated['alias']
        elif 'alias' in original and original['alias'] != '':
            name = ''
        elif 'name' in updated and updated['name'] != '':
            name = updated['name']

        if bi or name != '':
            livestate_db = current_app.data.driver.db['livestate']
            live_current = livestate_db.find_one({'service': original['_id']})
            data = {}
            if bi:
                data['business_impact'] = updated['business_impact']
            if name != '':
                data['display_name_service'] = name
            lookup = {"_id": live_current['_id']}
            patch_internal('livestate', data, False, False, **lookup)
