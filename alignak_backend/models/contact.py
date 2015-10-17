#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of contact
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'contact'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'schema': {
            'use': {
                'type': 'objectid',
                'ui': {
                    'title': 'Template(s)',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
            },
            'name': {
                'type': 'string',
                'title': 'Name',
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'definition_order': {
                'type': 'integer',
                'ui': {
                    'title': 'Definition order',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 100
            },
            'register': {
                'type': 'boolean',
                'ui': {
                    'title': 'Registered',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'contact_name': {
                'type': 'string',
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'required': True,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'alias': {
                'type': 'string',
                'ui': {
                    'title': 'Alias',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'contactgroups': {
                'type': 'list',
                'ui': {
                    'title': 'Contacts groups',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
            },
            'host_notifications_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Hosts notifications enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'service_notifications_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Services notifications enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'host_notification_period': {
                'type': 'objectid',
                'ui': {
                    'title': 'Hosts notifications period',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'service_notification_period': {
                'type': 'objectid',
                'ui': {
                    'title': 'Services notifications period',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'host_notification_options': {
                'type': 'list',
                'ui': {
                    'title': 'Hosts notifications options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": {
                        "list_type": "multichoices",
                        "list_allowed": {
                            u"d": u"Send notifications on Down state",
                            u"r": u"Send notifications on recoveries",
                            u"u": u"Send notifications on Unreachable state",
                            u"f": u"Send notifications on flapping start/stop",
                            u"s": u"Send notifications on scheduled downtime start/stop",
                            u"n": u"Do not send notifications"
                        }
                    }
                },
                'default': ['d', 'u', 'r', 'f', 's'],
                'allowed': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'service_notification_options': {
                'type': 'list',
                'ui': {
                    'title': 'Services notifications options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": {
                        "list_type": "multichoices",
                        "list_allowed": {
                            u"w": u"Send notifications on Warning state",
                            u"u": u"Send notifications on Unknown state",
                            u"c": u"Send notifications on Critical state",
                            u"r": u"Send notifications on recoveries",
                            u"f": u"Send notifications on flapping start/stop",
                            u"s": u"Send notifications on scheduled downtime start/stop",
                            u"n": u"Do not send notifications"
                        }
                    }
                },
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'allowed': ['w', 'u', 'c', 'r', 'f', 's', 'n']
            },
            'host_notification_commands': {
                'type': 'list',
                'ui': {
                    'title': 'Hosts notifications command',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
            },
            'service_notification_commands': {
                'type': 'list',
                'ui': {
                    'title': 'Services notifications command',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'command',
                        'embeddable': True,
                    }
                },
            },
            'min_business_impact': {
                'type': 'integer',
                'ui': {
                    'title': 'Minimum business impact',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 0
            },
            'email': {
                'type': 'string',
                'ui': {
                    'title': 'e-mail',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'pager': {
                'type': 'string',
                'ui': {
                    'title': 'Pager/Mobile',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address1': {
                'type': 'string',
                'ui': {
                    'title': 'Address',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address2': {
                'type': 'string',
                'ui': {
                    'title': 'Address (2)',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address3': {
                'type': 'string',
                'ui': {
                    'title': 'Address (3)',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address4': {
                'type': 'string',
                'ui': {
                    'title': 'Address (4)',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address5': {
                'type': 'string',
                'ui': {
                    'title': 'Address (5)',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'address6': {
                'type': 'string',
                'ui': {
                    'title': 'Address (6)',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'can_submit_commands': {
                'type': 'boolean',
                'ui': {
                    'title': 'Can submit commands',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'is_admin': {
                'type': 'boolean',
                'ui': {
                    'title': 'Administrator',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'expert': {
                'type': 'boolean',
                'ui': {
                    'title': 'Expert',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'retain_status_information': {
                'type': 'boolean',
                'ui': {
                    'title': 'Retain status information',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'retain_nonstatus_information': {
                'type': 'boolean',
                'ui': {
                    'title': 'Retain non status information',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'notificationways': {
                'type': 'list',
                'ui': {
                    'title': 'Notification ways',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'password': {
                'type': 'string',
                'ui': {
                    'title': 'UI Password',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'NOPASSWORDSET'
            },
            'note': {
                'type': 'string',
                'ui': {
                    'title': 'Note',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'back_password': {
                'type': 'string',
                'ui': {
                    'title': 'Backend password',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'token': {
                'type': 'string',
                'ui': {
                    'title': 'Token',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'back_role_super_admin': {
                'type': 'boolean',
                'ui': {
                    'title': 'Backend super-administrator',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False,
                'required': True,
            },
            'back_role_admin': {
                'type': 'list',
                'ui': {
                    'title': 'Backend administrator',
                    'visible': False,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': [],
                'required': True,
            },
            # This to define if the object in this model are to be used in the UI
            'ui': {
                'type': 'boolean',
                'default': True,
                'required': False,

                # UI parameters for the objects
                'ui': {
                    'list_title': 'Contacts list (%d items)',
                    'page_title': 'Contact: %s',
                    'uid': 'contact_name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True
                }
            }
        }
    }
