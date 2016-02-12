#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of contactgroup
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'contactgroup'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'members': {
                'type': 'list',
                'ui': {
                    'title': 'Contact members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            'contactgroup_members': {
                'type': 'list',
                'ui': {
                    'title': 'Contactgroup members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
            },
            'name': {
                'type': 'string',
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'required': True,
                'unique': True
            },
            'alias': {
                'type': 'string',
                'ui': {
                    'title': 'Alias',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
        }
    }
