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
            hosts = host.find()
            for h in hosts:
                Livestate.on_inserted_host([h])
            service = current_app.data.driver.db['service']
            services = service.find()
            for s in services:
                Livestate.on_inserted_service([s])

    @staticmethod
    def on_inserted_host(items):
        """
            What to do when a new host is inserted in the live state ...
        """
        for index, item in enumerate(items):
            name = ''
            if 'display_name' in item and item['display_name'] != '':
                name = item['display_name']
            elif 'alias' in item and item['alias'] != '':
                name = item['alias']
            else:
                name = item['host_name']

            data = {'host_name': item['_id'], 'service_description': None, 'state': 'UP',
                    'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'UP', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': '', 'type': 'host',
                    'business_impact': item['business_impact'], 'display_name_host': name}
            if item['initial_state'] == 'd':
                data['state'] = 'DOWN'
                data['last_state'] = 'DOWN'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNREACHABLE'
                data['last_state'] = 'UNREACHABLE'
            post_internal("livestate", data)

    @staticmethod
    def on_inserted_service(items):
        """
            What to do when a new service is inserted in the live state ...
        """
        for index, item in enumerate(items):
            name = ''
            if 'display_name' in item and item['display_name'] != '':
                name = item['display_name']
            elif 'alias' in item and item['alias'] != '':
                name = item['alias']
            else:
                name = item['service_description']

            host_db = current_app.data.driver.db['host']
            host_info = host_db.find_one({'_id': item['host_name']})
            name_h = host_info['host_name']
            if 'alias' in host_info and host_info['alias'] != '':
                name_h = host_info['alias']
            if 'display_name' in host_info and host_info['display_name'] != '':
                name_h = host_info['display_name']

            data = {'host_name': item['host_name'], 'service_description': item['_id'],
                    'state': 'OK', 'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'OK', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': '', 'type': 'service',
                    'business_impact': item['business_impact'], 'display_name_service': name,
                    'display_name_host': name_h}
            if item['initial_state'] == 'w':
                data['state'] = 'WARNING'
                data['last_state'] = 'WARNING'
            elif item['initial_state'] == 'c':
                data['state'] = 'CRITICAL'
                data['last_state'] = 'CRITICAL'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNKNOWN'
                data['last_state'] = 'UNKNOWN'
            post_internal("livestate", data)

    @staticmethod
    def on_updated_host(updated, original):
        """
            Update field business_impact if changed
        """
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
        elif 'host_name' in updated and updated['host_name'] != '':
            name = updated['host_name']

        if bi or name != '':
            livestate_db = current_app.data.driver.db['livestate']
            live_current = livestate_db.find_one({'host_name': original['_id'],
                                                  'service_description': None})
            data = {}
            if bi:
                data['business_impact'] = updated['business_impact']
            if name != '':
                data['display_name_host'] = name
            lookup = {"_id": live_current['_id']}
            patch_internal('livestate', data, False, False, **lookup)
            if name != '':
                lives = livestate_db.find({'host_name': original['_id'], 'type': 'service'})
                data = {'display_name_host': name}
                for live in lives:
                    lookup = {"_id": live['_id']}
                    patch_internal('livestate', data, False, False, **lookup)

    @staticmethod
    def on_updated_service(updated, original):
        """
            Update field business_impact if changed
        """
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
        elif 'service_description' in updated and updated['service_description'] != '':
            name = updated['service_description']

        if bi or name != '':
            livestate_db = current_app.data.driver.db['livestate']
            live_current = livestate_db.find_one({'service_description': original['_id']})
            data = {}
            if bi:
                data['business_impact'] = updated['business_impact']
            if name != '':
                data['display_name_service'] = name
            lookup = {"_id": live_current['_id']}
            patch_internal('livestate', data, False, False, **lookup)
