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
            'start_time': {
                'type': 'integer',
                'default': 0
            },
            'end_time': {
                'type': 'integer',
                'default': 86400
            },
            'fixed': {
                'type': 'boolean',
                'default': True
            },
            'duration': {
                'type': 'integer',
                'default': 86400
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
            # but it is not yet to be considered as an effective acknowledgement
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
