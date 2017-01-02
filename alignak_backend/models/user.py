#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of user
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'user'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': 'unknown'
            },
            'name': {
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'alias': {
                'type': 'string',
                'default': '',
            },
            'tags': {
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
                'default': []
            },
            'notes': {
                'type': 'string',
                'default': '',
            },
            'customs': {
                'type': 'dict',
                'default': {}
            },
            'host_notifications_enabled': {
                'type': 'boolean',
                'default': True
            },
            'service_notifications_enabled': {
                'type': 'boolean',
                'default': True
            },
            'host_notification_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },
            'service_notification_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },
            'host_notification_options': {
                'type': 'list',
                'default': ['d', 'u', 'r', 'f', 's'],
                'allowed': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'service_notification_options': {
                'type': 'list',
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'allowed': ['w', 'u', 'c', 'r', 'f', 's', 'n']
            },
            'host_notification_commands': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
            },
            'service_notification_commands': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
            },
            'min_business_impact': {
                'type': 'integer',
                'default': 0
            },
            'email': {
                'type': 'string',
                'default': ''
            },
            'pager': {
                'type': 'string',
                'default': ''
            },
            'address1': {
                'type': 'string',
                'default': ''
            },
            'address2': {
                'type': 'string',
                'default': ''
            },
            'address3': {
                'type': 'string',
                'default': ''
            },
            'address4': {
                'type': 'string',
                'default': ''
            },
            'address5': {
                'type': 'string',
                'default': ''
            },
            'address6': {
                'type': 'string',
                'default': ''
            },
            # To be completed...
            'notificationways': {
                'type': 'list',
                'default': []
            },
            'can_submit_commands': {
                'type': 'boolean',
                'default': False
            },
            'is_admin': {
                'type': 'boolean',
                'default': False
            },
            'password': {
                'type': 'string',
                'default': 'NOPASSWORDSET'
            },
            'token': {
                'type': 'string',
                'default': ''
            },
            # Is super administrator
            'back_role_super_admin': {
                'type': 'boolean',
                'default': False
            },
            # Is allowed to update the elements live state
            'can_update_livestate': {
                'type': 'boolean',
                'default': False
            },
            # User preferences
            'ui_preferences': {
                'type': 'dict',
                'default': {},
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
                'default': [],
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
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
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
                'default': [],
            },
            '_is_template': {
                'type': 'boolean',
                'default': False
            },
            '_templates': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_template_fields': {
                'type': 'dict',
                'default': {}
            }
        }
    }
