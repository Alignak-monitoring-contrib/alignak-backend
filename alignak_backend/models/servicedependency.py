#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of servicedependency
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'servicedependency'


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
            'dependent_hosts': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
            },
            'dependent_hostgroups': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'services': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
            },
            'dependent_services': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
            },
            'hosts': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
            },
            'hostgroups': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'inherits_parent': {
                'type': 'boolean',
                'default': False
            },
            'execution_failure_criteria': {
                'type': 'list',
                'default': ['u', 'c', 'w'],
                'allowed': ['o', 'w', 'u', 'c', 'p', 'n']
            },
            'notification_failure_criteria': {
                'type': 'list',
                'default': ['u', 'c', 'w'],
                'allowed': ['o', 'w', 'u', 'c', 'p', 'n']
            },
            'dependency_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },
            'explode_hostgroup': {
                'type': 'boolean',
                'default': False
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
