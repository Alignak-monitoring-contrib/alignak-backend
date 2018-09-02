#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information for Alignak notifications (eg. reload configuration)
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak notifications"
    return 'alignak_notifications'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``alignak_notifications`` model is a cache used internally by the backend to store the
    notifications that must be sent out to the Alignak arbiter.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'internal_resource': True,
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            'event': {
                'schema_version': 1,
                'title': 'Notification event (creation, deletion,...)',
                'type': 'string',
                'required': True,
            },
            'parameters': {
                'schema_version': 1,
                'title': 'Notification parameters',
                'type': 'string',
                'default': '',
                'required': False
            },
            'notification': {
                'schema_version': 1,
                'title': 'Notification url',
                'type': 'string',
                'default': 'backend_notification',
                'required': False
            }
        },
        'schema_deleted': {}
    }
