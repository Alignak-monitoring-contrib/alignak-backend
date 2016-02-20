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
            'dependent_host_name': {
                'type': 'string'
            },
            'dependent_hostgroup_name': {
                'type': 'string',
                'default': ''
            },
            'dependent_service_description': {
                'type': 'string',
                'default': ''
            },
            'host_name': {
                'type': 'string'
            },
            'hostgroup_name': {
                'type': 'string',
                'default': 'unknown'
            },
            'inherits_parent': {
                'type': 'boolean',
                'default': False
            },
            'execution_failure_criteria': {
                'type': 'list',
                'default': ['n']
            },
            'notification_failure_criteria': {
                'type': 'list',
                'default': ['n']
            },
            'dependency_period': {
                'type': 'string',
                'default': ''
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
