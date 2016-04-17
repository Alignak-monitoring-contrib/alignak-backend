#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of host
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'uipref'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'type': {
                'type': 'string',
                'ui': {
                    'title': "Preference's type",
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': ''
            },
            'user': {
                'type': 'string',
                'ui': {
                    'title': "User name",
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': ''
            },
            'data': {
                'type': 'dict',
                'ui': {
                    'title': "Preference's dictionary",
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': []
            },
        }
    }
