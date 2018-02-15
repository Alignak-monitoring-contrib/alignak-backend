#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of servicegroup
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak services groups"
    return 'servicegroup'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``servicegroup`` model is used to group several hosts.

    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'mongo_indexes': {
            'index_updated': [('_updated', 1)],
            'index_name': [('name', 1)],
        },
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
                'title': 'Services group name',
                'comment': 'Unique services group name',
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
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
            'notes_url': {
                'schema_version': 1,
                'title': 'Notes URL',
                'comment': 'Element notes URL. Displayed in the Web UI as some URL to be '
                           'navigatesd. Note that a very specific text format must be used for '
                           'this field, see the Web UI documentation.',
                'type': 'string',
                'default': ''
            },
            'action_url': {
                'schema_version': 1,
                'title': 'Actions URL',
                'comment': 'Element actions URL. Displayed in the Web UI as some available '
                           'actions. Note that a very specific text format must be used for '
                           'this field, see the Web UI documentation.',
                'type': 'string',
                'default': ''
            },

            # Servicegroup specific
            'servicegroups': {
                'schema_version': 1,
                'title': 'Groups',
                'comment': 'List of the groups of this group',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'servicegroup',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            'services': {
                'schema_version': 1,
                'title': 'Members',
                'comment': 'List of the members of this group',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
                'default': []
            },

            # Automatically managed by the backend
            '_level': {
                'schema_version': 1,
                'title': 'Level',
                'comment': 'Level in the hierarchy',
                'type': 'integer',
                'default': 0,
            },
            '_parent': {
                'schema_version': 1,
                'title': 'Parent',
                'comment': 'Immediate parent in the hierarchy',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'servicegroup',
                    'embeddable': True
                },
                'nullable': True,
                'default': None
            },
            '_tree_parents': {
                'schema_version': 1,
                'title': 'Parents',
                'comment': 'List of parents in the hierarchy',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'servicegroup',
                        'embeddable': True,
                    }
                },
                'default': []
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
            },
        },
        'schema_deleted': {}
    }
