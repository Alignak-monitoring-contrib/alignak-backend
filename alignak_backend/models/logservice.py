#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of logservice
"""

def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'logservice'


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
            },
            'state': {
                'type': 'string',
                'default': 'UP',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN"]
            },
            'state_type': {
                'type': 'string',
                'default': 'HARD',
                'allowed': ["HARD", "SOFT"]
            },
            'acknowledged': {
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'type': 'integer',
                'default': None
            },
            'output': {
                'type': 'string',
                'default': None
            },
            'long_output': {
                'type': 'string',
                'default': None
            },
            'perf_data': {
                'type': 'string',
                'default': None
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
