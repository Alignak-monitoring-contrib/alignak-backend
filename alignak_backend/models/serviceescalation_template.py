#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Templates of serviceescalation
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'serviceescalation_template'


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
                'unique': True,
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'host_name': {
                'type': 'string',
            },
            'hostgroup_name': {
                'type': 'string',
            },
            'service_description': {
                'type': 'string',
            },
            'first_notification': {
                'type': 'integer',
            },
            'last_notification': {
                'type': 'integer',
            },
            'notification_interval': {
                'type': 'integer',
                'default': 30
            },
            'escalation_period': {
                'type': 'string',
                'default': ''
            },
            'escalation_options': {
                'type': 'list',
                'default': ['d', 'u', 'r', 'w', 'c']
            },
            'contacts': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                }
            },
            'contact_groups': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contactgroup',
                    'embeddable': True
                }
            },
            'first_notification_time': {
                'type': 'integer',
            },
            'last_notification_time': {
                'type': 'integer',
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
