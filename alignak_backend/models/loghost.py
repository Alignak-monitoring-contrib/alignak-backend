#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of loghost
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'loghost'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'host': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True,
            },
            'state': {
                'type': 'string',
                'default': 'UP',
                'allowed': ["UP", "DOWN", "UNREACHABLE"]
            },
            'state_type': {
                'type': 'string',
                'default': 'HARD',
                'allowed': ["HARD", "SOFT"]
            },
            'state_id': {
                'type': 'integer',
                'default': 0
            },
            'acknowledged': {
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'type': 'integer',
                'default': None
            },
            'last_state': {
                'type': 'string',
                'default': 'OK',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN", "UP", "DOWN", "UNREACHABLE"]
            },
            'output': {
                'type': 'string',
                'default': ''
            },
            'long_output': {
                'type': 'string',
                'default': ''
            },
            'perf_data': {
                'type': 'string',
                'default': ''
            },
            'latency': {
                'type': 'float',
                'default': 0.0
            },
            'execution_time': {
                'type': 'float',
                'default': 0.0
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
        }
    }
