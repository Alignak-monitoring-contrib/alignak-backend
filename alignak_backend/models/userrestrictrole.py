#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of userrestrictrole
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "User role restriction"
    return 'userrestrictrole'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``userrestrictrole`` model is an internal data model used to define the CRUD
    rights for an Alignak backend user.

    This allows to defined, for a user and a given realm, the create, read, update, and
    delete rights on each backend endpoint.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'user': {
                "title": "Concerned user",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'realm': {
                "title": "Concerned realm",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            'sub_realm': {
                "title": "Sub-realms",
                "comment": "Is this right applicable to the sub-realms of the realm?",
                'type': 'boolean',
                'default': False
            },
            'resource': {
                "title": "Concerned resource",
                "comment": "Resource concerned with the right",
                'type': 'string',
                'default': '*',
                'allowed': [
                    '*',
                    'actionacknowledge', 'actiondowntime', 'actionforcecheck',
                    'alignak', 'alignakdaemon',
                    'realm', 'command', 'timeperiod',
                    'user', 'usergroup', 'userrestrictrole',
                    'host', 'hostgroup', 'hostdependency', 'hostescalation',
                    'service', 'servicegroup', 'servicedependency', 'serviceescalation',
                    'grafana', 'graphite', 'influxdb', 'statsd',
                    'timeseriesretention',
                    'livesynthesis', 'livesynthesisretention',
                    'logcheckresult', 'history'
                ],
            },
            'crud': {
                "title": "Right",
                "comment": "User's right for the concerned resource in the concerned realm. "
                           "Use ``*`` if all resources are concerned.",
                'type': 'list',
                'default': ['read'],
                'allowed': ['create', 'read', 'update', 'delete', 'custom']
            },
        }
    }
