#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of downtime
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'actiondowntime'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'action': {
                'type': 'string',
                'default': 'OK',
                'allowed': ["add", "delete"]
            },
            'host': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True
            },
            'service': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'start_time': {
                'type': 'datetime',
                'required': True
            },
            'end_time': {
                'type': 'datetime',
                'nullable': True,
                'default': None
            },
            'fixed': {
                'type': 'boolean',
                'default': True
            },
            'duration': {
                'type': 'integer',
                'default': 86400
            },
            'trigger': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'trigger',
                    'embeddable': True
                },
                'nullable': True
            },
            'user': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'comment': {
                'type': 'string',
                'default': ''
            },
            'processed': {
                'type': 'boolean',
                'default': False
            }
        }
    }
