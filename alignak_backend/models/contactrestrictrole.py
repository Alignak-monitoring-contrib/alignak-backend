#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of contactrestrictrole
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'contactrestrictrole'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'contact': {
                'type': 'objectid',
                'ui': {
                    'title': 'COntact',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
                'required': True,
            },
            'realm': {
                'type': 'objectid',
                'ui': {
                    'title': 'Realm',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            'sub_realm': {
                'type': 'boolean',
                'ui': {
                    'title': 'Sub realm visibility',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': False
            },
            'resource': {
                'type': 'string',
                'ui': {
                    'title': 'Resource name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'required': True,
            },
            'crud': {
                'type': 'string',
                'ui': {
                    'title': 'CRUD rights',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': 'read',
                'required': True,
                'allowed': ['create', 'read', 'update', 'delete', 'custom']
            },
        }
    }
