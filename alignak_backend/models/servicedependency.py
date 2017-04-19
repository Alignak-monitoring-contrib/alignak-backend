#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of servicedependency
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Service dependency"
    return 'servicedependency'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``servicedependency`` model is used to define dependency relations and tests conditions.

    See the Alignak documentation regarding the dependency check management.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            # Importation source
            'imported_from': {
                "title": "Imported from",
                "comment": "Item importation source (alignak-backend-import, ...)",
                'type': 'string',
                'default': 'unknown'
            },
            'definition_order': {
                "title": "Definition order",
                "comment": "Priority level if several elements have the same name",
                'type': 'integer',
                'default': 100
            },

            # Identity
            'name': {
                "title": "Service dependency name",
                'type': 'string',
                'empty': False,
                'unique': True
            },
            'alias': {
                "title": "Alias",
                "comment": "Element friendly name used by the Web User Interface.",
                'type': 'string',
                'default': ''
            },
            'notes': {
                "title": "Notes",
                "comment": "Element notes. Free text to store element information.",
                'type': 'string',
                'default': ''
            },

            'dependent_hosts': {
                "title": "Dependent hosts",
                "comment": "List of the hosts that are depending.",
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
                "title": "Dependent hosts groups",
                "comment": "List of the hosts groups that are depending.",
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
                "title": "Services",
                "comment": "List of the services involved in the dependency.",
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
                "title": "Dependent services",
                "comment": "List of the services that are depending.",
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
                "title": "Hosts",
                "comment": "List of the hosts involved in the dependency.",
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
                "title": "Hosts groups",
                "comment": "List of the hosts groups involved in the dependency.",
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
                "title": "Parent inheritance",
                "comment": "See Alginak doc about dependency checks.",
                'type': 'boolean',
                'default': False
            },
            'execution_failure_criteria': {
                "title": "Execution criteria",
                "comment": "See Alginak doc about dependency checks.",
                'type': 'list',
                'default': ['u', 'c', 'w'],
                'allowed': ['o', 'w', 'u', 'c', 'p', 'n']
            },
            'notification_failure_criteria': {
                "title": "Notification criteria",
                "comment": "See Alginak doc about dependency checks.",
                'type': 'list',
                'default': ['u', 'c', 'w'],
                'allowed': ['o', 'w', 'u', 'c', 'p', 'n']
            },
            'dependency_period': {
                "title": "Dependency period",
                "comment": "Time period during which the dependency checks are done.",
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

            # Realm
            '_realm': {
                "title": "Realm",
                "comment": "Realm this element belongs to.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                "title": "Sub-realms",
                "comment": "Is this element visible in the sub-realms of its realm?",
                'type': 'boolean',
                'default': True
            },

            # Users CRUD permissions
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
