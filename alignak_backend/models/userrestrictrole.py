#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of userrestrictrole
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'userrestrictrole'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'user': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            'sub_realm': {
                'type': 'boolean',
                'default': False
            },
            'resource': {
                'type': 'string',
                'default': '*',
                'allowed': ['*', 'host', 'service', 'command'],
                'required': True,
            },
            'crud': {
                'type': 'list',
                'default': ['read'],
                'allowed': ['create', 'read', 'update', 'delete', 'custom']
            },
        }
    }
