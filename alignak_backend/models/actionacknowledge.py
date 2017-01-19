#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of acknowledge
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'actionacknowledge'


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
                'default': 'add',
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
            'sticky': {
                'type': 'boolean',
                'default': True
            },
            'notify': {
                'type': 'boolean',
                'default': False
            },
            'persistent': {
                'type': 'boolean',
                'default': True
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
            # The action has been set on the host/service by Alignak and it can be
            # considered as effective if processed is True
            'processed': {
                'type': 'boolean',
                'default': False
            },
            # The action has been fetched by the Alignak arbiter if notified is True
            # but it is not yet to be considered as an effective scheduled downtime
            'notified': {
                'type': 'boolean',
                'default': False
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                }
            },
            '_sub_realm': {
                'type': 'boolean',
                'default': False
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
        }
    }
