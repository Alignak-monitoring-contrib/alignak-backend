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
        'auth_field': 'u_id',
        'allow_unknown': True,
        'schema': {
            'type': {
                'type': 'string',
                'default': ''
            },
            'user': {
                'type': 'string',
                'default': ''
            },
            'data': {
                'type': 'dict',
                'default': []
            },
        }
    }
