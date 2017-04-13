#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of realm
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak realm"
    return 'realm'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``realm`` model is used to represent a realm of the monitored system.

    The Alignak framework distributed architecture allows to have a unique Alignak instance to
    manage a huge system. I nsuch a cas, it is interesting to be able to cut this huge
    configuration into parts for different sites, customers, ... For Alignak, those parts are
    **realms**.

    A realm is a group of resources (hosts ) tha users will be able to manage. All resources in
    the Alignak backend are attached to a realm. At minimum, it is the *All* realm that always
    exist in any Alignak instance.

    The realm organization is hierarchical. A realm may have sub-realms that also may have
    sub-realms. Sub-realms visibility of the resources allow the Alignak backend users to view
    the resources defined in upper realms.
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
                "title": "Realm name",
                "comment": "Unique realm name",
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
                'regex': r"^[a-zA-Z0-9 \-_]+$",
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

            'default': {
                "title": "Default realm",
                "comment": "This realm is the default realm used when no realm information "
                           "is provided.",
                'type': 'boolean',
                'default': False
            },

            # todo: check whether this is really useful :/
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
                "title": "Parent",
                "comment": "Immediate parent in the hierarchy",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
            },
            '_tree_parents': {
                "title": "Parents",
                "comment": "List of parents in the hierarchy",
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
                "title": "Children",
                "comment": "List of the immediate children in the hierarchy",
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
                "title": "Children",
                "comment": "List of all the children in the hierarchy",
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
                "title": "Level",
                "comment": "Level in the hierarchy",
                'type': 'integer',
                'default': 0,
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
