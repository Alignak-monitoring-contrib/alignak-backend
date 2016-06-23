#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of history
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'history'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'host': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True,
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
            'user': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'nullable': True
            },
            'type': {
                'type': 'string',
                'required': True,
                'allowed': [
                    # WebUI user comment
                    "webui.comment",

                    # Check result
                    "check.result",

                    # Request to force a check
                    "check.request",
                    "check.requested",

                    # Add acknowledge
                    "ack.add",
                    # Set acknowledge
                    "ack.processed",
                    # Delete acknowledge
                    "ack.delete",

                    # Add downtime
                    "downtime.add",
                    # Set downtime
                    "downtime.processed",
                    # Delete downtime
                    "downtime.delete"
                ],
                'default': 'check.result'
            },
            'message': {
                'type': 'string',
                'default': ''
            },
            'logcheckresult': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'logcheckresult',
                    'embeddable': True
                },
                'required': False,
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
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
