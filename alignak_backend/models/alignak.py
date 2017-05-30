#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of Alignak
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak configuration"
    return 'alignak'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``alignak`` model is used to store the global configuration of an Alignak instance.

    """


def get_schema():
    """Schema structure of this resource

    Some fields are defined  but this resource allows to store some other fields that may be some
    macros definition.

    Note that the `name` field is 1) not unique, 2) used as a reference for the Arbiter match.

    The configuration for an Alignak Arbiter named as 'arbiter-master' may be dispatched into
    several items in this collection with the same name field.

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'name': {
                "title": "Alignak name",
                "comment": "Alignak instance name. This will be compared to the Alignak arbiter "
                           "instance name to get the correct configuration.",
                'type': 'string',
                'required': True,
                'unique': False,
                'empty': False,
            },
            'alias': {
                'type': 'string',
                'default': ''
            },
            'notes': {
                'type': 'string',
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                'default': ''
            },

            # Global Alignak status
            'instance_name': {
                "title": "Instance name",
                "comment": "Reporting daemon name",
                'type': 'string'
            },

            'pid': {
                "title": "Instance PID",
                "comment": "Reporting daemon PID",
                'type': 'integer',
                'default': 0
            },

            'program_start': {
                "title": "Program start time",
                "comment": "",
                'type': 'integer',
                'default': 0
            },

            # Global Alignak configuration
            'interval_length': {
                "title": "Application interval length",
                "comment": "Default is 60 seconds for one minute",
                'type': 'integer',
                'default': 60
            },

            # Global Alignak configuration
            'notifications_enabled': {
                "title": "Notifications enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'flap_detection_enabled': {
                "title": "Flapping detection enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'event_handlers_enabled': {
                "title": "Event handlers enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },
            'global_host_event_handler': {
                "title": "Global host event handler",
                "comment": "Command that will be used as an event handler "
                           "if none is specified for a specific host/service.",
                'type': 'string',
                'default': 'None'
            },
            'global_service_event_handler': {
                "title": "Global service event handler",
                "comment": "Command that will be used as an event handler "
                           "if none is specified for a specific host/service.",
                'type': 'string',
                'default': 'None'
            },

            # todo: deprecate this according to Alignak
            'process_performance_data': {
                "title": "Process performance data",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'passive_host_checks_enabled': {
                "title": "Passive host checks enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },
            'passive_service_checks_enabled': {
                "title": "Passive service checks enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'active_host_checks_enabled': {
                "title": "Active host checks enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },
            'active_service_checks_enabled': {
                "title": "Active service checks enabled",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'check_external_commands': {
                "title": "Check external commands",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            'check_host_freshness': {
                "title": "Check host checks freshness",
                "comment": "",
                'type': 'boolean',
                'default': True
            },
            'check_service_freshness': {
                "title": "Check service checks freshness",
                "comment": "",
                'type': 'boolean',
                'default': True
            },

            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
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
