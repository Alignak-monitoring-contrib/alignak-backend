#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of alignakretention
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Host/service data retention from scheduler of Alignak'
    return 'alignakretention'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``alignakretention`` model is used by the Alignak backend scheduler module for the
    Alignak retention feature.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'auth_field': '_user',
        'item_methods': ['GET', 'PATCH', 'PUT', 'DELETE'],
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            'host': {
                'schema_version': 1,
                'type': 'string',
            },
            '_user': {
                'schema_version': 1,
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
            }
        },
        'schema_deleted': {}
    }
