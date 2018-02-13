#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of timeperiod
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak time period"
    return 'timeperiod'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``timeperiod`` model is used to represent time periods in the monitored system.

    Time periods are used in many situations:

    - for the hosts and services active/passive checks. Outside of the defined time periods,
    Alignak will not try to determine the hosts/services states.

    - for the notifications. The notifications will be sent-out only during the defined
    time periods.

    A time period is built with time ranges for each day of the week that "rotate" once the
    week has ended. Different types of exceptions to the normal weekly time are supported,
    including: specific weekdays, days of generic months, days of specific months,
    and calendar dates.
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
                'title': 'Time period name',
                'comment': 'Unique time period name',
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

            # Timeperiod specific
            'dateranges': {
                'schema_version': 1,
                'title': 'Date ranges',
                'comment': 'List of date ranges',
                'type': 'list',
                'default': []
            },
            'exclude': {
                'schema_version': 1,
                'title': 'Exclusions',
                'comment': 'List of excluded ranges.',
                'type': 'list',
                'default': []
            },

            # todo: really manage this...
            'is_active': {
                'schema_version': 1,
                'title': 'Active',
                'comment': 'The timeperiod is currently active or inactive.',
                'type': 'boolean',
                'default': False
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
