#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of realm
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'realm'


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
                'regex': r"^[a-zA-Z0-9 \-_]+$",
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'alias': {
                'type': 'string',
                'default': '',
            },
            'notes': {
                'type': 'string',
                'default': '',
            },
            'default': {
                'type': 'boolean',
                'default': False
            },
            'hosts_critical_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 5
            },
            'hosts_warning_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 3
            },
            'services_critical_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 5
            },
            'services_warning_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 3
            },
            'global_critical_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 5
            },
            'global_warning_threshold': {
                'type': 'integer',
                'min': 0,
                'max': 100,
                'default': 3
            },
            '_parent': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                # 'required': True,
            },
            '_tree_parents': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'realm',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_children': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'realm',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_all_children': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'realm',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_level': {
                'type': 'integer',
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
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
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
            },
        }
    }
