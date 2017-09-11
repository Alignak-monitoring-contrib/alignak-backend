#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of history
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Events log"
    return 'history'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``history`` model is used to maintain a log of the received checks results.

    The Alignak backend stores all the checks results it receives to keep a full log of the system
    checks results.
    """


def get_schema():
    """Schema structure of this resource

    host/service define the concerned host/service for this history event. If the service is null
    then the event is an host event. When posting an history the backend will value the host_name
    and service_name fields automatically, this to keep human readable information even when the
    host/service do not exist anymore in the backend or if host/service _id got changed (host
    deleted and re-created).

    The type field defines the event type (see the type definition for the allowed events)

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'host': {
                "title": "Concerned host identifier",
                "comment": "! Will be removed in a future version",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'nullable': True
            },
            'host_name': {
                "title": "Concerned host name",
                "comment": "The backend stores the host name. This allows to keep "
                           "an information about the concerned host even if it "
                           "has been deleted from the backend.",
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'service': {
                "title": "Concerned service identifier",
                "comment": "! Will be removed in a future version",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'nullable': True
            },
            'service_name': {
                "title": "Concerned service name",
                "comment": "The backend stores the service name. This allows to keep "
                           "an information about the concerned service even if it "
                           "has been deleted from the backend.",
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'user': {
                "title": "Concerned user identifier",
                "comment": "! Will be removed in a future version",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'nullable': True
            },
            'user_name': {
                "title": "Concerned user name",
                "comment": "The backend stores the user name. This allows to keep "
                           "an information about the concerned user even if it "
                           "has been deleted from the backend.",
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'type': {
                "title": "History event type",
                'type': 'string',
                'required': True,
                'allowed': [
                    # WebUI user comment
                    "webui.comment",

                    # Check result
                    "check.result",

                    # Request to force a check
                    "check.request",
                    "check.requested",

                    # Add acknowledge
                    "ack.add",
                    # Set acknowledge
                    "ack.processed",
                    # Delete acknowledge
                    "ack.delete",

                    # Add downtime
                    "downtime.add",
                    # Set downtime
                    "downtime.processed",
                    # Delete downtime
                    "downtime.delete",

                    # external command
                    "monitoring.external_command",

                    # timeperiod transition
                    "monitoring.timeperiod_transition",
                    # alert
                    "monitoring.alert",
                    # event handler
                    "monitoring.event_handler",
                    # flapping start / stop
                    "monitoring.flapping_start",
                    "monitoring.flapping_stop",
                    # downtime start / cancel / end
                    "monitoring.downtime_start",
                    "monitoring.downtime_cancelled",
                    "monitoring.downtime_end",
                    # acknowledge
                    "monitoring.acknowledge",
                    # notification
                    "monitoring.notification",
                ],
                'default': 'check.result'
            },
            'message': {
                "title": "History event message",
                'type': 'string',
                'default': ''
            },
            'logcheckresult': {
                "title": "Relate log chek result (if any)",
                "comment": "This relation is only valid if the event type is a check result",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'logcheckresult',
                    'embeddable': True
                },
                'required': False,
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
            },
            '_sub_realm': {
                'type': 'boolean',
                'default': True
            },
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
