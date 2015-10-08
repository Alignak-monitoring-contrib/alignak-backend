#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ``alignak_backend.livestate`` module

    This module manages the livestate
"""
from __future__ import print_function
from flask import current_app, g, request, abort, jsonify


class Livestate(object):

    def __init__(self, app):
        self.app = app

    @staticmethod
    def on_inserted_host(items):
        for index, item in enumerate(items):
            data = {'host_name': item['_id'], 'service_description': None, 'state': 'UP',
                    'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'UP', 'last_state_type': 'HARD', 'output': None,
                    'long_output': None, 'perf_data': None}
            if item['initial_state'] == 'd':
                data['state'] = 'DOWN'
                data['last_state'] = 'DOWN'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNREACHABLE'
                data['last_state'] = 'UNREACHABLE'
            current_app.data.insert('livestate', [data])

    @staticmethod
    def on_inserted_service(items):
        for index, item in enumerate(items):
            data = {'host_name': item['host_name'], 'service_description': item['_id'],
                    'state': 'OK', 'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                    'last_state': 'OK', 'last_state_type': 'HARD', 'output': None,
                    'long_output': None, 'perf_data': None}
            if item['initial_state'] == 'w':
                data['state'] = 'WARNING'
                data['last_state'] = 'WARNING'
            elif item['initial_state'] == 'c':
                data['state'] = 'CRITICAL'
                data['last_state'] = 'CRITICAL'
            elif item['initial_state'] == 'u':
                data['state'] = 'UNKNOWN'
                data['last_state'] = 'UNKNOWN'
            current_app.data.insert('livestate', [data])
