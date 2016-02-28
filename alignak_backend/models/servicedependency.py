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
                'type': 'list',
                'ui': {
                    'title': 'Dependent hosts names',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": "link"
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'dependent_hostgroup_name': {
                'type': 'list',
                'ui': {
                    'title': 'Dependent hostgroups names',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": "link"
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'dependent_service_description': {
                'type': 'list',
                'ui': {
                    'title': 'Dependent services names',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": "link"
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
            },
            'host_name': {
                'type': 'list',
                'ui': {
                    'title': 'Hosts names',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": "link"
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
            },
            'hostgroup_name': {
                'type': 'list',
                'ui': {
                    'title': 'Hostgroups names',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": "link"
                },
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
