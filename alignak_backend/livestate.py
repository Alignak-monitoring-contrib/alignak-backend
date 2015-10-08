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
        livestate = current_app.data.driver.db['livestate']
        for index, item in enumerate(items):
            input = {'host_name': item['id'], 'service_description': None, 'state': 'UP',
                     'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                     'last_state': 'UP', 'last_state_type': 'HARD', 'output': None,
                     'long_output': None, 'perf_data': None}
            if item['initial_state'] == 'd':
                input['state'] = 'DOWN'
                input['last_state'] = 'DOWN'
            elif item['initial_state'] == 'u':
                input['state'] = 'UNREACHABLE'
                input['last_state'] = 'UNREACHABLE'
            livestate.add(input)

    @staticmethod
    def on_inserted_service(items):
        livestate = current_app.data.driver.db['livestate']
        for index, item in enumerate(items):
            input = {'host_name': item['host_name'], 'service_description': item['id'],
                     'state': 'OK', 'state_type': 'HARD', 'acknowledged': False, 'last_check': 0,
                     'last_state': 'OK', 'last_state_type': 'HARD', 'output': None,
                     'long_output': None, 'perf_data': None}
            if item['initial_state'] == 'w':
                input['state'] = 'WARNING'
                input['last_state'] = 'WARNING'
            elif item['initial_state'] == 'c':
                input['state'] = 'CRITICAL'
                input['last_state'] = 'CRITICAL'
            elif item['initial_state'] == 'u':
                input['state'] = 'UNKNOWN'
                input['last_state'] = 'UNKNOWN'
            livestate.add(input)
