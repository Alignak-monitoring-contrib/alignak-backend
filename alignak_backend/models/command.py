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
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'required': True,
                'unique': True,
            },
            'definition_order': {
                'type': 'integer',
                'ui': {
                    'title': 'Definition order',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 100
            },
            'command_line': {
                'type': 'string',
                'ui': {
                    'title': 'Command line',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
            },
            'poller_tag': {
                'type': 'string',
                'ui': {
                    'title': 'Poller tag',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'None'
            },
            'reactionner_tag': {
                'type': 'string',
                'ui': {
                    'title': 'Reactionner tag',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'None'
            },
            'module_type': {
                'type': 'string',
                'ui': {
                    'title': 'Module type',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'fork'
            },
            'timeout': {
                'type': 'integer',
                'ui': {
                    'title': 'Timeout',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': -1
            },
            'enable_environment_macros': {
                'type': 'boolean',
                'ui': {
                    'title': 'Environment macros',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            '_realm': {
                'type': 'objectid',
                'ui': {
                    'title': 'Realm',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'type': 'boolean',
                'ui': {
                    'title': 'Readable on sub realms',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
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
                'default': [],
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
                'default': [],
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
                'default': [],
            },
            # This to define if the object in this model are to be used in the UI
            'ui': {
                'type': 'boolean',
                'default': True,
                'required': False,

                # UI parameters for the objects
                'ui': {
                    'list_title': 'Commands list (%d items)',
                    'page_title': 'Command: %s',
                    'uid': 'command_name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True
                }
            }
        }
    }
