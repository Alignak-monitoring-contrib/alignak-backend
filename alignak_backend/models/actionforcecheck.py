#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of forcecheck
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Check request'
    return 'actionforcecheck'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``actionforcecheck`` contains the checks requested and processed.

    To ask for a forced check for an host/service the client post on this endpoint to create a new
    re-check request that will be managed by the Alignak backend Broker module to build an
    external command notified to the Alignak framework.

    **Note** that the Alignak Web Services module allow to use more external commands.
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
            'host': {
                'schema_version': 1,
                'title': 'Host',
                'comment': 'The host concerned by the acknowledge.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True
            },
            'service': {
                'schema_version': 1,
                'title': 'Service',
                'comment': 'The service concerned by the acknowledge.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'user': {
                'schema_version': 1,
                'title': 'User',
                'comment': 'The user concerned by the acknowledge.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'comment': {
                'schema_version': 1,
                'title': 'Comment',
                'comment': 'The comment of the acknowledge action. Free text.',
                'type': 'string',
                'default': ''
            },

            'processed': {
                'schema_version': 1,
                'title': 'Processed',
                'comment': 'The action has been set on the host/service by Alignak and it can '
                           'be considered as effective if processed is True',
                'type': 'boolean',
                'default': False
            },

            # Realm
            '_realm': {
                'schema_version': 1,
                'title': 'Realm',
                'comment': 'Realm this element belongs to. Note that this property will always '
                           'be forced to the value of the concerned host realm.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                }
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
        },
        'schema_deleted': {}
    }
