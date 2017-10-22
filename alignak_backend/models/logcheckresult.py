#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of logcheckresult
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return 'Check result log'
    return 'logcheckresult'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``logcheckresult`` model is used to maintain a log of the received checks results.

    The Alignak backend stores all the checks results it receives to keep a full log of the system
    checks results.
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
                'title': 'Concerned host',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True,
            },
            'host_name': {
                'schema_version': 1,
                'title': 'Host name',
                'comment': 'The backend stores the host name. This allows to keep '
                           'an information about the concerned host even if it '
                           'has been deleted from the backend.',
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'service': {
                'schema_version': 1,
                'title': 'Concerned service',
                'comment': 'If not set, this check result is an host check',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'service_name': {
                'schema_version': 1,
                'title': 'Service name',
                'comment': 'The backend stores the service name. This allows to keep '
                           'an information about the concerned service even if it '
                           'has been deleted from the backend.',
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'state': {
                'schema_version': 1,
                'title': 'State',
                'type': 'string',
                'allowed': ['UP', 'DOWN', 'UNREACHABLE', 'OK', 'WARNING', 'CRITICAL', 'UNKNOWN'],
                'required': True,
            },
            'state_type': {
                'schema_version': 1,
                'title': 'State type',
                'type': 'string',
                'allowed': ['HARD', 'SOFT'],
                'required': True,
            },
            'state_id': {
                'schema_version': 1,
                'title': 'State identifier',
                'type': 'integer',
                'default': 0
            },
            'passive_check': {
                'schema_version': 1,
                'title': 'Passive check',
                'type': 'boolean',
                'default': False
            },
            'acknowledged': {
                'schema_version': 1,
                'title': 'Acknowledged',
                'type': 'boolean',
                'default': False
            },
            'acknowledgement_type': {
                'schema_version': 1,
                'title': 'Acknowledgement type',
                'type': 'integer',
                'default': 1
            },
            'downtimed': {
                'schema_version': 1,
                'title': 'Downtimed',
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'schema_version': 1,
                'title': 'Check timestamp',
                'type': 'integer',
                'default': 0
            },
            'last_state': {
                'schema_version': 1,
                'title': 'Last state',
                'type': 'string',
                'default': 'OK',
                'allowed': ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN', 'UP', 'DOWN', 'UNREACHABLE']
            },
            'last_state_type': {
                'schema_version': 1,
                'title': 'Last state type',
                'type': 'string',
                'allowed': ['HARD', 'SOFT'],
                'required': True,
            },
            'last_state_id': {
                'schema_version': 1,
                'title': 'Last state identifier',
                'type': 'integer',
                'default': 0
            },
            'last_state_changed': {
                'schema_version': 1,
                'title': 'Last state changed',
                'type': 'integer',
                'default': 0
            },
            'state_changed': {
                'schema_version': 1,
                'title': 'State changed',
                'type': 'boolean',
                'default': False
            },
            'output': {
                'schema_version': 1,
                'title': 'Output',
                'type': 'string',
                'default': ''
            },
            'long_output': {
                'schema_version': 1,
                'title': 'Long output',
                'type': 'string',
                'default': ''
            },
            'perf_data': {
                'schema_version': 1,
                'title': 'Performance data',
                'type': 'string',
                'default': ''
            },
            'latency': {
                'schema_version': 1,
                'title': 'Latency',
                'type': 'float',
                'default': 0.0
            },
            'execution_time': {
                'schema_version': 1,
                'title': 'Execution time',
                'type': 'float',
                'default': 0.0
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
        },
        'schema_deleted': {}
    }
