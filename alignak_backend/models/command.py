#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of command
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak command"
    return 'command'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``command`` model is used to represent a command in the monitored system.

    A command is used:

    - for the hosts and services active checks. The command is a check plugin
    used to determine the host or service state.

    - for the event handlers launched when an host / service state changes.

     - for the notifications sent to inform the users of the detected problems
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            # Importation source
            'imported_from': {
                "title": "Imported from",
                "comment": "Item importation source (alignak-backend-import, ...)",
                'type': 'string',
                'default': 'unknown'
            },
            'definition_order': {
                "title": "Definition order",
                "comment": "Priority level if several elements have the same name",
                'type': 'integer',
                'default': 100
            },

            # Identity
            'name': {
                "title": "Command name",
                "comment": "Unique command name",
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
            },
            'alias': {
                "title": "Alias",
                "comment": "Element friendly name used by the Web User Interface.",
                'type': 'string',
                'default': ''
            },
            'notes': {
                "title": "Notes",
                "comment": "Element notes. Free text to store element information.",
                'type': 'string',
                'default': ''
            },

            # Command specific
            'command_line': {
                "title": "Command line",
                "comment": "System command executed to run the command.",
                'type': 'string',
            },
            'module_type': {
                "title": "Module type",
                "comment": "A specific module type may be defined to associate commands "
                           "to a dedicated worker. To be completed...",
                'type': 'string',
                'default': 'fork'
            },
            'timeout': {
                "title": "Timeout",
                "comment": "Maximum command execution time before ALignak force the command stop.",
                'type': 'integer',
                'default': -1
            },
            'enable_environment_macros': {
                "title": "Environment macros",
                "comment": "Set Alignak environment macros before running this command.",
                'type': 'boolean',
                'default': False
            },

            # Alignak daemons
            'poller_tag': {
                "title": "Poller tag",
                "comment": "Set a value for this element checks to be managed by a "
                           "dedicated poller.",
                'type': 'string',
                'default': ''
            },
            'reactionner_tag': {
                "title": "Reactionner tag",
                "comment": "Set a value for this element notifications to be managed by a "
                           "dedicated reactionner.",
                'type': 'string',
                'default': ''
            },

            # Realm
            '_realm': {
                "title": "Realm",
                "comment": "Realm this element belongs to.",
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
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
