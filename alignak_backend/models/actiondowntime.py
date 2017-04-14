#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of downtime
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Downtimes"
    return 'actiondowntime'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``actiondowntime`` contains the downtimes requested and processed.

    To schedule a downtime for an host/service the client post on this endpoint to create a new
    downtime request that will be managed by the Alignak backend Broker module to build an
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
            'action': {
                "title": "Action",
                "comment": "Use 'add' to add a new downtime, or "
                           "'delete' to delete an downtime",
                'type': 'string',
                'default': 'add',
                'allowed': ["add", "delete"]
            },

            'host': {
                "title": "Host",
                "comment": "The host concerned by the downtime.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True
            },
            'service': {
                "title": "Service",
                "comment": "The service concerned by the downtime.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
                'nullable': True
            },
            'user': {
                "title": "User",
                "comment": "The user concerned by the downtime.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'comment': {
                "title": "Comment",
                "comment": "The comment of the downtime action. Free text.",
                'type': 'string',
                'default': ''
            },

            'processed': {
                "title": "Processed",
                "comment": "The action has been set on the host/service by Alignak and it can "
                           "be considered as effective if processed is True",
                'type': 'boolean',
                'default': False
            },
            'notified': {
                "title": "Notified",
                "comment": "The action has been fetched by the Alignak arbiter if notified is "
                           "True but it is not yet to be considered as an effective "
                           "scheduled downtime",
                'type': 'boolean',
                'default': False
            },

            'start_time': {
                "title": "Start time",
                "comment": "The ``start_time`` and ``end_time`` properties are specified in "
                           "time_t format (seconds since the UNIX epoch).",
                'type': 'integer',
                'default': 0
            },
            'end_time': {
                "title": "End time",
                "comment": "The ``start_time`` and ``end_time`` properties are specified in "
                           "time_t format (seconds since the UNIX epoch).",
                'type': 'integer',
                'default': 86400
            },
            'fixed': {
                "title": "Fixed",
                "comment": "If the ``fixed`` argument is set, the downtime will start and end "
                           "at the times specified by the ``start_time`` and ``end_time`` "
                           "properties. Otherwise, the downtime will begin between the "
                           "``start_time`` and ``end_time`` times and will last for "
                           "``duration`` seconds.",
                'type': 'boolean',
                'default': True
            },
            'duration': {
                "title": "Duration",
                "comment": "The ``duration`` property is used when the ``fixed`` property "
                           "is not set.",
                'type': 'integer',
                'default': 86400
            },

            # Realm
            '_realm': {
                "title": "Realm",
                "comment": "Realm this element belongs to. Note that this property will always "
                           "be forced to the value of the concerned host realm.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                }
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
        }
    }
