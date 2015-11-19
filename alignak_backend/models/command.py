#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of command
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'command'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'name': {
                'type': 'string',
                'required': True,
                'unique': True,
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'command_line': {
                'type': 'string'
            },
            'poller_tag': {
                'type': 'string',
                'default': 'None'
            },
            'reactionner_tag': {
                'type': 'string',
                'default': 'None'
            },
            'module_type': {
                'type': 'string',
                'default': 'fork'
            },
            'timeout': {
                'type': 'integer',
                'default': -1
            },
            'enable_environment_macros': {
                'type': 'boolean',
                'default': False
            },
            '_brotherhood': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'brotherhood',
                        'embeddable': True,
                    }
                },
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_create': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_delete': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
        }
    }
