#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of Alignak daemons
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Alignak daemons live state'
    return 'alignakdaemon'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``alignakdaemon`` model is maintained by Alignak to provide the live state of
    the Alignak daemons.

    For hosts and services, the live synthesis stores values computed from the real
    live state, each time an element state is updated:
    - a counter containing the number of host/service in each state
    - a counter containing the number of host/service acknowledged
    - a counter containing the number of host/service in downtime
    - a counter containing the number of host/service flapping
    - the maximum business impact of the host/service in the state
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
            'name': {
                'schema_version': 1,
                'title': 'Daemon name',
                'comment': 'Unique daemon name',
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'address': {
                'schema_version': 1,
                'title': 'Address',
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'port': {
                'schema_version': 1,
                'title': 'Port',
                'type': 'integer',
                'required': True,
                'empty': False,
            },
            'last_check': {
                'schema_version': 1,
                'title': 'Last check',
                'comment': 'Last time the daemon was checked',
                'type': 'integer',
                'required': True,
                'empty': False,
            },
            'alive': {
                'schema_version': 1,
                'title': 'Alive',
                'comment': 'The daemon is alive',
                'type': 'boolean',
                'required': True,
                'default': False
            },
            'reachable': {
                'schema_version': 1,
                'title': 'Reachable',
                'comment': 'The daemon is reachable',
                'type': 'boolean',
                'required': True,
                'default': False
            },
            'passive': {
                'schema_version': 1,
                'title': 'Passive',
                'comment': 'The daemon is a passive daemon',
                'type': 'boolean',
                'required': True,
                'default': False
            },
            'spare': {
                'schema_version': 1,
                'title': 'Spare',
                'comment': 'The daemon is a spare daemon',
                'type': 'boolean',
                'required': True,
                'default': False
            },
            'type': {
                'schema_version': 1,
                'title': 'Type',
                'comment': 'Daemon type: "arbiter", "scheduler", "poller", '
                           '"broker", "reactionner", "receiver"',
                'type': 'string',
                'required': True,
                'allowed': ['arbiter', 'scheduler', 'poller', 'broker', 'reactionner', 'receiver']
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
