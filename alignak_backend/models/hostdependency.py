#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of hostdependency
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Host dependency'
    return 'hostdependency'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``hostdependency`` model is used to define dependency relations and tests conditions.

    See the Alignak documentation regarding the dependency check management.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            # Importation source
            'imported_from': {
                'schema_version': 1,
                'title': 'Imported from',
                'comment': 'Item importation source (alignak-backend-import, ...)',
                'type': 'string',
                'default': 'unknown'
            },
            'definition_order': {
                'schema_version': 1,
                'title': 'Definition order',
                'comment': 'Priority level if several elements have the same name',
                'type': 'integer',
                'default': 100
            },

            # Identity
            'name': {
                'schema_version': 1,
                'title': 'Host dependency name',
                'type': 'string',
                'empty': False,
                'unique': True
            },
            'alias': {
                'schema_version': 1,
                'title': 'Alias',
                'comment': 'Element friendly name used by the Web User Interface.',
                'type': 'string',
                'default': ''
            },
            'notes': {
                'schema_version': 1,
                'title': 'Notes',
                'comment': 'Element notes. Free text to store element information.',
                'type': 'string',
                'default': ''
            },

            'dependent_hosts': {
                'schema_version': 1,
                'title': 'Dependent hosts',
                'comment': 'List of the hosts that are depending.',
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
                'schema_version': 1,
                'title': 'Dependent hosts groups',
                'comment': 'List of the hosts groups that are depending.',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'hosts': {
                'schema_version': 1,
                'title': 'Hosts',
                'comment': 'List of the hosts involved in the dependency.',
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
                'schema_version': 1,
                'title': 'Hosts groups',
                'comment': 'List of the hosts groups involved in the dependency.',
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
                'schema_version': 1,
                'title': 'Parent inheritance',
                'comment': 'See Alginak doc about dependency checks.',
                'type': 'boolean',
                'default': False
            },
            'execution_failure_criteria': {
                'schema_version': 1,
                'title': 'Execution criteria',
                'comment': 'See Alginak doc about dependency checks.',
                'type': 'list',
                'default': ['n'],
                'allowed': ['o', 'd', 'x', 'p', 'n']
            },
            'notification_failure_criteria': {
                'schema_version': 1,
                'title': 'Notification criteria',
                'comment': 'See Alginak doc about dependency checks.',
                'type': 'list',
                'default': ['d', 'u', 'p'],
                'allowed': ['o', 'd', 'x', 'p', 'n']
            },
            'dependency_period': {
                'schema_version': 1,
                'title': 'Dependency period',
                'comment': 'Time period during which the dependency checks are done.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },

            # Realm
            '_realm': {
                'schema_version': 1,
                'title': 'Realm',
                'comment': 'Realm this element belongs to.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'schema_version': 1,
                'title': 'Sub-realms',
                'comment': 'Is this element visible in the sub-realms of its realm?',
                'type': 'boolean',
                'default': True
            },

            # Users CRUD permissions
            '_users_read': {
                'schema_version': 1,
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
                'schema_version': 1,
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
                'schema_version': 1,
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            }
        },
        'schema_deleted': {}
    }
