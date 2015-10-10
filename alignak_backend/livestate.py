#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.livestate`` module

    This module manages the livestate
"""
from __future__ import print_function
from flask import current_app, g, request, abort, jsonify
from eve.methods.post import post_internal


class Livestate(object):

    @staticmethod
    def recalculate():
        livestate = current_app.data.driver.db['livestate']
        if livestate.count() == 0:
            host = current_app.data.driver.db['host']
            hosts = host.find()
            Livestate.on_inserted_host(hosts)
            service = current_app.data.driver.db['service']
            services = service.find()
            Livestate.on_inserted_service(services)

    @staticmethod
    def on_inserted_host(items):
        for index, item in enumerate(items):
            data = {'host_name': item['_id'], 'service_description': None, 'state': 'UP',
                    'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'UP', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': ''}
            if item['initial_state'] == 'd':
                data['state'] = 'DOWN'
                data['last_state'] = 'DOWN'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNREACHABLE'
                data['last_state'] = 'UNREACHABLE'
            # current_app.data.insert('livestate', [data])
            post_internal("livestate", data)

    @staticmethod
    def on_inserted_service(items):
        for index, item in enumerate(items):
            data = {'host_name': item['host_name'], 'service_description': item['_id'],
                    'state': 'OK', 'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'OK', 'last_state_type': 'HARD', 'output': '',
                    'long_output': '', 'perf_data': ''}
            if item['initial_state'] == 'w':
                data['state'] = 'WARNING'
                data['last_state'] = 'WARNING'
            elif item['initial_state'] == 'c':
                data['state'] = 'CRITICAL'
                data['last_state'] = 'CRITICAL'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNKNOWN'
                data['last_state'] = 'UNKNOWN'
            # current_app.data.insert('livestate', [data])
            post_internal("livestate", data)
