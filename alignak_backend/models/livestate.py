#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of livestate
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'livestate'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'schema': {
            'service_description': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'host_name': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'state': {
                'type': 'string',
                'default': 'OK',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN", "UP", "DOWN", "UNREACHABLE"]
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
            'downtime': {
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'type': 'integer',
                'default': 0
            },
            'last_state': {
                'type': 'string',
                'default': 'OK',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN", "UP", "DOWN", "UNREACHABLE"]
            },
            'last_state_type': {
                'type': 'string',
                'default': 'HARD',
                'allowed': ["HARD", "SOFT"]
            },
            'last_state_changed': {
                'type': 'integer',
                'default': 0
            },
            'next_check': {
                'type': 'integer',
                'default': 0
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
            'current_attempt': {
                'type': 'integer',
                'default': 0
            },
            'max_attempts': {
                'type': 'integer',
                'default': 0
            },
            'business_impact': {
                'type': 'integer',
                'default': 2
            },
            '_brotherhood': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'brotherhood',
                        'embeddable': True,
                    }
                },
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_create': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_delete': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
        }
    }
