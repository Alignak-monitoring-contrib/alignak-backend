#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of acknowledge
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Acknowledges"
    return 'actionacknowledge'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``actionacknowledge`` contains the acknowledgement requested and processed.

    To acknowledge an host/service problem the client post on this endpoint to create a new
    acknowledge request that will be managed by the Alignak backend Broker module to build an
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
                "comment": "Use 'add' to add a new acknowledge, or "
                           "'delete' to delete an acknowledge",
                'type': 'string',
                'default': 'add',
                'allowed': ["add", "delete"]
            },

            'host': {
                "title": "Host",
                "comment": "The host concerned by the acknowledge.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True
            },
            'service': {
                "title": "Service",
                "comment": "The service concerned by the acknowledge.",
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
                "comment": "The user concerned by the acknowledge.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user',
                    'embeddable': True
                },
                'required': True,
            },
            'comment': {
                "title": "Comment",
                "comment": "The comment of the acknowledge action. Free text.",
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

            'sticky': {
                "title": "Sticky",
                "comment": "If the sticky option is set, the acknowledgement will remain "
                           "until the host/service recovers. Otherwise the acknowledgement "
                           "will automatically be removed when the host/service state changes.",
                'type': 'boolean',
                'default': True
            },
            'notify': {
                "title": "Notify",
                "comment": "If the notify option is set, a notification will be sent out "
                           "to contacts indicating that the current host/service problem has "
                           "been acknowledged, else there will be no notification.",
                'type': 'boolean',
                'default': False
            },
            'persistent': {
                "title": "Persistent",
                "comment": "Alignak always consider an acknowledge as persistent. Thus this "
                           "property is of no importance and it will be removed in a future "
                           "version.",
                'type': 'boolean',
                'default': True
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
