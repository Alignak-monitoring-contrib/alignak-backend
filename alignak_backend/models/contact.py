#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of contact
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'contact'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'schema': {
            'use': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
            },
            'name': {
                'type': 'string',
                'default': ''
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'register': {
                'type': 'boolean',
                'default': True
            },
            'contact_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'alias': {
                'type': 'string',
                'default': ''
            },
            'contactgroups': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
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
                }
            },
            'service_notification_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'host_notification_options': {
                'type': 'list',
                'default': []
            },
            'service_notification_options': {
                'type': 'list',
                'default': []
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
            'can_submit_commands': {
                'type': 'boolean',
                'default': False
            },
            'is_admin': {
                'type': 'boolean',
                'default': False
            },
            'expert': {
                'type': 'boolean',
                'default': False
            },
            'retain_status_information': {
                'type': 'boolean',
                'default': True
            },
            'retain_nonstatus_information': {
                'type': 'boolean',
                'default': True
            },
            'notificationways': {
                'type': 'list',
                'default': []
            },
            'password': {
                'type': 'string',
                'default': 'NOPASSWORDSET'
            },
            'note': {
                'type': 'string',
                'default': ''
            },
            'back_password': {
                'type': 'string',
                'default': ''
            },
            'back_role_super_admin': {
                'type': 'boolean',
                'default': False,
                'required': True,
            },
            'back_role_admin': {
                'type': 'list',
                'default': [],
                'required': True,
            },
        }
    }
