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

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'schema': {
            'contact': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
                'required': True,
            },
            'brotherhood': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'brotherhood',
                    'embeddable': True
                },
                'required': True,
            },
            'resource': {
                'type': 'list',
                'default': [],
                'required': True,
            },
        }
    }
