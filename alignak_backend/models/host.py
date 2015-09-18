#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of host
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'host'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'imported_from': {
                'type': 'string',
                '_title': 'Import source',
                'default': ''
            },
            'use': {
                'type': 'objectid',
                '_title': 'Template(s)',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
            },
            'name': {
                'type': 'string',
                '_title': 'Name',
                'default': ''
            },
            'definition_order': {
                'type': 'integer',
                '_title': 'Definition order',
                'default': 100
            },
            'register': {
                'type': 'boolean',
                '_title': 'Registered',
                'default': True
            },
            'host_name': {
                'type': 'string',
                '_title': 'Host name',
                'required': True,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$'
            },
            'alias': {
                'type': 'string',
                '_title': 'Alias',
                'default': ''
            },
            'display_name': {
                'type': 'string',
                '_title': 'Display name',
                'default': ''
            },
            'address': {
                'type': 'string',
                '_title': 'Address',
                'default': ''
            },
            'parents': {
                'type': 'list',
                '_title': 'Parents',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
            },
            'hostgroups': {
                'type': 'list',
                '_title': 'Hosts groups',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },
            'check_command': {
                'type': 'objectid',
                '_title': 'Check command',
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                }
            },
            'check_command_args': {
                'type': 'string',
                '_title': 'Check command arguments',
                'default': ''
            },
            'initial_state': {
                'type': 'string',
                '_title': 'Initial state',
                'minlength': 1,
                'maxlength': 1,
                'default': 'u',
                'allowed': ["u", "d", "u"]
            },
            'max_check_attempts': {
                'type': 'integer',
                '_title': 'Max check attempts',
                'default': 1
            },
            'check_interval': {
                'type': 'integer',
                '_title': 'Check interval',
                'default': 5
            },
            'retry_interval': {
                'type': 'integer',
                '_title': 'Retry interval',
                'default': 0
            },
            'active_checks_enabled': {
                'type': 'boolean',
                '_title': 'Active checks enabled',
                'default': True
            },
            'passive_checks_enabled': {
                'type': 'boolean',
                '_title': 'Passive checks enabled',
                'default': True
            },
            'check_period': {
                'type': 'objectid',
                '_title': 'Check period',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'check_freshness': {
                'type': 'boolean',
                '_title': 'Check freshness',
                'default': False
            },
            'freshness_threshold': {
                'type': 'integer',
                '_title': 'Freshness threshold',
                'default': 0
            },
            'event_handler': {
                'type': 'string',
                '_title': 'Event handler',
                'default': ''
            },
            'event_handler_enabled': {
                'type': 'boolean',
                '_title': 'Event handler enabled',
                'default': False
            },
            'low_flap_threshold': {
                'type': 'integer',
                '_title': 'Low flapping threshold',
                'default': 25
            },
            'high_flap_threshold': {
                'type': 'integer',
                '_title': 'High flapping threshold',
                'default': 50
            },
            'flap_detection_enabled': {
                'type': 'boolean',
                '_title': 'Flapping detection enabled',
                'default': True
            },
            'flap_detection_options': {
                'type': 'list',
                '_title': 'Flpping detection options',
                'default': ['o', 'd', 'u'],
                'possible': ['o', 'd', 'u']
            },
            'process_perf_data': {
                'type': 'boolean',
                '_title': 'Process performance data',
                'default': True
            },
            'retain_status_information': {
                'type': 'boolean',
                '_title': 'Retain status information',
                'default': True
            },
            'retain_nonstatus_information': {
                'type': 'boolean',
                '_title': 'Retain non status information',
                'default': True
            },
            'contacts': {
                'type': 'list',
                '_title': 'Contact(s)',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            'contact_groups': {
                'type': 'list',
                '_title': 'Contacts group(s)',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
            },
            'notification_interval': {
                'type': 'integer',
                '_title': 'Notification interval',
                'default': 60
            },
            'first_notification_delay': {
                'type': 'integer',
                '_title': 'First notification delay',
                'default': 0
            },
            'notification_period': {
                'type': 'objectid',
                '_title': 'Notification period',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'notification_options': {
                'type': 'list',
                '_title': 'Notification options',
                'default': ['d', 'u', 'r', 'f', 's'],
                'possible': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'notifications_enabled': {
                'type': 'boolean',
                '_title': 'Notifications enabled',
                'default': True
            },
            'stalking_options': {
                'type': 'list',
                '_title': 'Stalking options',
                'default': [],
                'possible': ['o', 'd', 'u']
            },
            'notes': {
                'type': 'string',
                '_title': 'Notes',
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                '_title': 'Notes URL',
                'default': ''
            },
            'action_url': {
                'type': 'string',
                '_title': 'Action URL',
                'default': ''
            },
            'icon_image': {
                'type': 'string',
                '_title': 'Icon image',
                'default': ''
            },
            'icon_image_alt': {
                'type': 'string',
                '_title': 'Icon image alt',
                'default': ''
            },
            'icon_set': {
                'type': 'string',
                '_title': 'Icon set',
                'default': ''
            },
            'vrml_image': {
                'type': 'string',
                '_title': 'VRML image',
                'default': ''
            },
            'statusmap_image': {
                'type': 'string',
                '_title': 'Status map image',
                'default': ''
            },
            '2d_coords': {
                'type': 'string',
                '_title': '2D coordinates',
                'default': ''
            },
            '3d_coords': {
                'type': 'string',
                '_title': '3D coordinates',
                'default': ''
            },
            'failure_prediction_enabled': {
                'type': 'boolean',
                '_title': 'Failure prediction enabled',
                'default': False
            },
            'realm': {
                'type': 'string',
                '_title': 'Realm',
                'default': None
            },
            'poller_tag': {
                'type': 'string',
                '_title': 'Poller tag',
                'default': 'None'
            },
            'reactionner_tag': {
                'type': 'string',
                '_title': 'Reactionner tag',
                'default': 'None'
            },
            'resultmodulations': {
                'type': 'list',
                '_title': 'Result modulations',
                'default': []
            },
            'business_impact_modulations': {
                'type': 'list',
                '_title': 'Business impact modulations',
                'default': []
            },
            'escalations': {
                'type': 'list',
                '_title': 'Escalations',
                'default': [],
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'escalation',
                        'embeddable': True,
                    }
                },
            },
            'maintenance_period': {
                'type': 'string',
                '_title': 'Maintenance period',
                'default': ''
            },
            'time_to_orphanage': {
                'type': 'integer',
                '_title': 'Time to orphanage',
                'default': 300
            },
            'service_overrides': {
                'type': 'list',
                '_title': 'Service overrides',
                'default': []
            },
            'service_excludes': {
                'type': 'list',
                '_title': 'Service excludes',
                'default': []
            },
            'service_includes': {
                'type': 'list',
                '_title': 'Service includes',
                'default': []
            },
            'labels': {
                'type': 'list',
                '_title': 'Buiness rules labels',
                'default': []
            },
            'business_rule_output_template': {
                'type': 'string',
                '_title': 'Business rules output template',
                'default': ''
            },
            'business_rule_smart_notifications': {
                'type': 'boolean',
                '_title': 'Business rules smart notifications',
                'default': False
            },
            'business_rule_downtime_as_ack': {
                'type': 'boolean',
                '_title': 'Business rules downtime as ack',
                'default': False
            },
            'business_rule_host_notification_options': {
                'type': 'list',
                '_title': 'Business rules host notification options',
                'default': ['d', 'u', 'r', 'f', 's'],
                'possible': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'business_rule_service_notification_options': {
                'type': 'list',
                '_title': 'Business rules service notification options',
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'possible': ['w', 'u', 'c', 'r', 'f', 's', 'n']
            },
            'business_impact': {
                'type': 'integer',
                '_title': 'Business impact',
                'default': 2
            },
            'trigger': {
                'type': 'string',
                '_title': 'Trigger',
                'default': ''
            },
            'trigger_name': {
                'type': 'string',
                '_title': 'Trigger name',
                'default': ''
            },
            'trigger_broker_raise_enabled': {
                'type': 'boolean',
                '_title': 'Trigger broker raise enabled',
                'default': False
            },
            'trending_policies': {
                'type': 'list',
                '_title': 'Trending policies',
                'default': []
            },
            'checkmodulations': {
                'type': 'list',
                '_title': 'Check modulations',
                'default': []
            },
            'macromodulations': {
                'type': 'list',
                '_title': 'Macro modulations',
                'default': []
            },
            'custom_views': {
                'type': 'list',
                '_title': 'Custom views',
                'default': []
            },
            'snapshot_enabled': {
                'type': 'boolean',
                '_title': 'Snapshot enabled',
                'default': False
            },
            'snapshot_command': {
                'type': 'string',
                '_title': 'Snapshot command',
                'default': ''
            },
            'snapshot_period': {
                'type': 'string',
                '_title': 'Snapshot period',
                'default': ''
            },
            'snapshot_criteria': {
                'type': 'list',
                '_title': 'Snapshot criteria',
                'default': ['d', 'u']
            },
            'snapshot_interval': {
                'type': 'integer',
                '_title': 'Snapshot interval',
                'default': 5
            },
            '_brotherhood': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'brotherhood',
                        'embeddable': True,
                    }
                },
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_create': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            '_users_delete': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
        }
    }
