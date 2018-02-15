#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of user
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Alignak user"
    return 'user'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``user`` model is used to represent a user involved in the monitored system.

    It may be a "real" user that will be notified about the problems detected by Alignak, or
    a user that will use the Web User Interface to view information, or, even, a system or
    program user that will connect to the Alginak backend to provide information.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'mongo_indexes': {
            'index_updated': [('_updated', 1)],
            'index_tpl': [('_is_template', 1)],
            'index_name': [('name', 1)],
        },
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 2,
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
                'title': 'User name',
                'comment': 'Unique user name. Will be used as a login username',
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
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
            'tags': {
                'schema_version': 1,
                'title': 'Tags',
                'comment': 'List of tags for this element. Intended to set tags by the Web UI',
                'type': 'list',
                'schema': {
                    'type': 'string',
                },
                'default': []
            },
            'customs': {
                'schema_version': 1,
                'title': 'Custom variables',
                'comment': '',
                'type': 'dict',
                'default': {}
            },

            # User specific
            'skill_level': {
                'schema_version': 1,
                'title': 'Level',
                'comment': "This field is the user's skill level. It is used by the Web User "
                           "Interface to display more or less advanced information. Each property "
                           "in the backend data models may have its own skill level and it will "
                           "be displayed it the user's skill level is greater than or equal. "
                           "As default, the skill level is 0 and the property will be displayed.",
                'type': 'integer',
                'default': 0,
                'min': 0,
                'max': 2
            },
            'password': {
                'schema_version': 1,
                'title': 'Password',
                'comment': "This field is used on user's creation as the password and it is "
                           "then obfuscated by the Alignak backend",
                'type': 'string',
                'default': 'NOPASSWORDSET'
            },
            'token': {
                'schema_version': 1,
                'title': 'Token',
                'comment': "This field is the user's authentication token that can be used in "
                           "the REST API as a basic authentication credentials",
                'type': 'string',
                'default': ''
            },

            # User preferences
            'ui_preferences': {
                'schema_version': 1,
                'title': 'User preferences',
                'comment': 'User preferences that are used by the Web User Interface to manage '
                           'the user preferences (eg. table filters, ...).',
                'type': 'dict',
                'default': {},
            },

            # User roles
            'back_role_super_admin': {
                'schema_version': 1,
                'title': 'Super administrator',
                'comment': 'This user is a super-administrator that is allowed to view and do '
                           'anything in the Alignak backend',
                'type': 'boolean',
                'default': False
            },
            'can_update_livestate': {
                'schema_version': 1,
                'title': 'Can update livestate',
                'comment': 'This user can update the live state information of the Alignak '
                           'backend. This property is used for the user that will be configured '
                           'for the Alignak Broker backend module. If this attribute is not set, '
                           'then the logged-in user will not be allowed to update live state '
                           'information (standard Web User Interface user).',
                'type': 'boolean',
                'skill_level': 2,
                'default': False
            },
            'is_admin': {
                'schema_version': 1,
                'title': 'Administrator',
                'comment': 'Used by the Web User Interface to allow the logged-in user to update '
                           'the Alignak backend data and to send commands to Alignak',
                'type': 'boolean',
                'default': False
            },
            'can_submit_commands': {
                'schema_version': 1,
                'title': 'Can submit commands',
                'comment': 'Used by the Web User Interface to allow the logged-in user to send '
                           'commands to Alignak. This do not allow the user to edit the Alignak '
                           'backend data.',
                'type': 'boolean',
                'default': False
            },
            'webui_visible': {
                'schema_version': 2,
                'title': 'Web UI visible',
                'comment': 'If not set, the Web User Interface will ignore this user.',
                'type': 'boolean',
                'default': True
            },

            'min_business_impact': {
                'schema_version': 1,
                'title': 'Minimum business impact',
                'comment': 'Minimum business impact the user is concerned with. '
                           'If a notification is raised for an element which BI is lower than '
                           'the minimum business impact of the user, the notification will be '
                           'filtered out.',
                'type': 'integer',
                'skill_level': 1,
                'default': 0
            },
            'email': {
                'schema_version': 1,
                'title': 'e-mail address',
                'comment': 'User e-mail address to be used for the notifications.',
                'type': 'string',
                'default': ''
            },
            'pager': {
                'schema_version': 1,
                'title': 'Mobile',
                'comment': 'User mobile phone to be used for the notifications.',
                'type': 'string',
                'default': ''
            },
            # todo: replace all host fields with address / postcode / ...
            'address1': {
                'schema_version': 1,
                'title': 'Address 1',
                'comment': 'User post address.',
                'type': 'string',
                'default': ''
            },
            'address2': {
                'schema_version': 1,
                'title': 'Address 2',
                'comment': 'User post address.',
                'type': 'string',
                'default': ''
            },
            'address3': {
                'schema_version': 1,
                'title': 'Address 3',
                'comment': 'User post address.',
                'type': 'string',
                'default': ''
            },
            'address4': {
                'schema_version': 1,
                'title': 'Address 4',
                'comment': 'User post address.',
                'type': 'string',
                'default': ''
            },
            'address5': {
                'schema_version': 1,
                'title': 'Address 5',
                'comment': 'User post address.',
                'type': 'string',
                'default': ''
            },
            'address6': {
                'schema_version': 1,
                'title': 'Address 6',
                'comment': "User post address. Note that this field may be used in the "
                           "configuration files when importing data into the Alignak backend. "
                           "The alignak-backend-import script will consider this field as "
                           "the user's realm.",
                'type': 'string',
                'default': ''
            },

            # Notifications
            'host_notifications_enabled': {
                'schema_version': 1,
                'title': 'Host notifications enabled',
                'comment': 'If unset, this user will never receive any notification when a '
                           'problem is detected for an host/service he is linked to.',
                'type': 'boolean',
                'default': False
            },
            'host_notification_period': {
                'schema_version': 1,
                'title': 'Host notifications period',
                'comment': 'Time period defining the moments this user will receive the '
                           'notifications raised or an element he is attached to.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },
            'host_notification_options': {
                'schema_version': 1,
                'title': 'Host notifications options',
                'comment': 'List of the notifications types that can be sent.',
                'type': 'list',
                'default': ['d', 'u', 'r', 'f', 's'],
                'allowed': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'host_notification_commands': {
                'schema_version': 1,
                'title': 'Host notifications commands',
                'comment': 'List of the notifications commands used to send the notifications.',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
                'nullable': True
            },

            'service_notifications_enabled': {
                'schema_version': 1,
                'title': 'Service notifications enabled',
                'comment': 'If unset, this user will never receive any notification when a '
                           'problem is detected for an host/service he is linked to.',
                'type': 'boolean',
                'default': False
            },
            'service_notification_period': {
                'schema_version': 1,
                'title': 'Service notifications period',
                'comment': 'Time period defining the moments this user will receive the '
                           'notifications raised or an element he is attached to.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'required': True,
            },
            'service_notification_options': {
                'schema_version': 1,
                'title': 'Service notifications options',
                'comment': 'List of the notifications types that can be sent.',
                'type': 'list',
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'allowed': ['w', 'u', 'c', 'r', 'f', 's', 'n']
            },
            'service_notification_commands': {
                'schema_version': 1,
                'title': 'Service notifications commands',
                'comment': 'List of the notifications commands used to send the notifications.',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
                'nullable': True
            },

            # todo: not yet implemented (see #103)
            'notificationways': {
                'schema_version': 1,
                'title': 'Notification ways',
                'comment': 'User notification ways.',
                'type': 'list',
                'skill_level': 2,
                'default': []
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

            # Templates
            '_is_template': {
                'schema_version': 1,
                'title': 'Template',
                'comment': 'Indicate if this element is a template or a real element',
                'type': 'boolean',
                'default': False
            },
            '_templates': {
                'schema_version': 1,
                'title': 'Templates',
                'comment': 'List of templates this element is linked to.',
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_template_fields': {
                'schema_version': 1,
                'title': 'Template fields',
                'comment': 'If this element is not a template, this field contains the list of '
                           'the fields linked to the templates this element is linked to',
                'type': 'list',
                'default': []
            },
        },
        'schema_deleted': {}
    }
