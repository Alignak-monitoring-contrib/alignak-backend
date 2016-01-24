#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of service
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'service'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'imported_from': {
                'type': 'string',
                'ui': {
                    'title': 'Import source',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'name': {
                'type': 'string',
                'ui': {
                    'title': 'Service name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'required': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$',
                'dependencies': ['host_name', 'check_command']
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
            'host_name': {
                'type': 'objectid',
                'ui': {
                    'title': 'Host name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
            },
            'hostgroup_name': {
                'type': 'string',
                'ui': {
                    'title': 'Hosts group name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
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
            'display_name': {
                'type': 'string',
                'ui': {
                    'title': 'Display name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'servicegroups': {
                'type': 'list',
                'ui': {
                    'title': 'Service group(s)',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'servicegroup',
                        'embeddable': True,
                    }
                },
            },
            'is_volatile': {
                'type': 'boolean',
                'ui': {
                    'title': 'Volatile',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'check_command': {
                'type': 'objectid',
                'ui': {
                    'title': 'Check command',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                },
                'allowed': ['bp_rule'],
                'nullable': True
            },
            'check_command_args': {
                'type': 'string',
                'ui': {
                    'title': 'Check command arguments',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'initial_state': {
                'type': 'string',
                'ui': {
                    'title': 'Initial state',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'minlength': 1,
                'maxlength': 1,
                'default': 'o',
                'allowed': ["o", "w", "c", "u"]
            },
            'max_check_attempts': {
                'type': 'integer',
                'ui': {
                    'title': 'Max check attempts',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 1
            },
            'check_interval': {
                'type': 'integer',
                'ui': {
                    'title': 'Check interval',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 5
            },
            'retry_interval': {
                'type': 'integer',
                'ui': {
                    'title': 'Retry interval',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 0
            },
            'active_checks_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Active checks enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'passive_checks_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Passive checks enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'check_period': {
                'type': 'objectid',
                'ui': {
                    'title': 'Check period',
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
            'check_freshness': {
                'type': 'boolean',
                'ui': {
                    'title': 'Check freshness',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'freshness_threshold': {
                'type': 'integer',
                'ui': {
                    'title': 'Freshness threshold',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 0
            },
            'event_handler': {
                'type': 'string',
                'ui': {
                    'title': 'Event handler',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'event_handler_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Event handler enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'low_flap_threshold': {
                'type': 'integer',
                'ui': {
                    'title': 'Low flapping threshold',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': -1
            },
            'high_flap_threshold': {
                'type': 'integer',
                'ui': {
                    'title': 'High flapping threshold',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': -1
            },
            'flap_detection_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Flapping detection enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'flap_detection_options': {
                'type': 'list',
                'ui': {
                    'title': 'Flapping detection options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": {
                        "list_type": "multichoices",
                        "list_allowed": {
                            u"o": u"Up",
                            u"w": u"Warning",
                            u"c": u"Critical",
                            u"u": u"Unknown"
                        }
                    }
                },
                'default': ['o', 'w', 'c', 'u']
            },
            'process_perf_data': {
                'type': 'boolean',
                'ui': {
                    'title': 'Process performance data',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
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
            'notification_interval': {
                'type': 'integer',
                'ui': {
                    'title': 'Notification interval',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 60
            },
            'first_notification_delay': {
                'type': 'integer',
                'ui': {
                    'title': 'First notification delay',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 0
            },
            'notification_period': {
                'type': 'objectid',
                'ui': {
                    'title': 'Notification period',
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
            'notification_options': {
                'type': 'list',
                'ui': {
                    'title': 'Notification options',
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
                            u"n": u"Do not send notifications"
                        }
                    }
                },
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'allowed': ['w', 'u', 'c', 'r', 'f', 's']
            },
            'notifications_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Notification enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'contacts': {
                'type': 'list',
                'ui': {
                    'title': 'Contact(s)',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
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
                'ui': {
                    'title': 'Contacts group(s)',
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
            'stalking_options': {
                'type': 'list',
                'ui': {
                    'title': 'Stalking options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": {
                        "list_type": "multichoices",
                        "list_allowed": {
                            u"o": u"Ok",
                            u"w": u"Warning",
                            u"c": u"Critical",
                            u"u": u"Unknown"
                        }
                    }
                },
                'default': [],
                'allowed': ['o', 'w', 'u', 'c']
            },
            'notes': {
                'type': 'string',
                'ui': {
                    'title': 'Notes',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                'ui': {
                    'title': 'Notes URL',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'action_url': {
                'type': 'string',
                'ui': {
                    'title': 'Action URL',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'icon_image': {
                'type': 'string',
                'ui': {
                    'title': 'Icon image',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'icon_image_alt': {
                'type': 'string',
                'ui': {
                    'title': 'Icon image alt',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'icon_set': {
                'type': 'string',
                'ui': {
                    'title': 'Icon set',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'failure_prediction_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Failure prediction enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'parallelize_check': {
                'type': 'boolean',
                'ui': {
                    'title': 'Parallelize checks',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'poller_tag': {
                'type': 'string',
                'ui': {
                    'title': 'Poller tag',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'None'
            },
            'reactionner_tag': {
                'type': 'string',
                'ui': {
                    'title': 'Reactionner tag',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 'None'
            },
            'resultmodulations': {
                'type': 'list',
                'ui': {
                    'title': 'Result modulations',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'business_impact_modulations': {
                'type': 'list',
                'ui': {
                    'title': 'Business impact modulations',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'escalations': {
                'type': 'list',
                'ui': {
                    'title': 'Escalations',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'escalation',
                        'embeddable': True,
                    }
                },
            },
            'maintenance_period': {
                'type': 'objectid',
                'ui': {
                    'title': 'Maintenance period',
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
            'time_to_orphanage': {
                'type': 'integer',
                'ui': {
                    'title': 'Time to orphanage',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 300
            },
            'merge_host_contacts': {
                'type': 'boolean',
                'ui': {
                    'title': 'Merge host contacts',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'labels': {
                'type': 'list',
                'ui': {
                    'title': 'Labels',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'host_dependency_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Host dependency enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': True
            },
            'business_rule_output_template': {
                'ui': {
                    'title': 'Business rule output template',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'type': 'string'
            },
            'business_rule_smart_notifications': {
                'type': 'boolean',
                'ui': {
                    'title': 'Business rule smart notifications',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'business_rule_downtime_as_ack': {
                'type': 'boolean',
                'ui': {
                    'title': 'Business rule downtime as ack',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'business_rule_host_notification_options': {
                'type': 'list',
                'ui': {
                    'title': 'Business rule host notification options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'business_rule_service_notification_options': {
                'type': 'list',
                'ui': {
                    'title': 'Business rule service notification options',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'service_dependencies': {
                'type': 'list',
                'ui': {
                    'title': 'Service dependencies',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
            },
            'duplicate_foreach': {
                'type': 'string',
                'ui': {
                    'title': 'Duplicate foreach',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'default_value': {
                'type': 'string',
                'ui': {
                    'title': 'Default value',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'business_impact': {
                'type': 'integer',
                'ui': {
                    'title': 'Business impact',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 2
            },
            'trigger': {
                'type': 'string',
                'ui': {
                    'title': 'Trigger',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'trigger_name': {
                'type': 'string',
                'ui': {
                    'title': 'Trigger name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'trigger_broker_raise_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Trigger broker raise enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'trending_policies': {
                'type': 'list',
                'ui': {
                    'title': 'Trending policies',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'checkmodulations': {
                'type': 'list',
                'ui': {
                    'title': 'Check modulations',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'macromodulations': {
                'type': 'list',
                'ui': {
                    'title': 'Macro modulations',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'custom_views': {
                'type': 'list',
                'ui': {
                    'title': 'Custom views',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': []
            },
            'aggregation': {
                'type': 'string',
                'ui': {
                    'title': 'Aggregation',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'snapshot_enabled': {
                'type': 'boolean',
                'ui': {
                    'title': 'Snapshot enabled',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': False
            },
            'snapshot_command': {
                'type': 'string',
                'ui': {
                    'title': 'Snapshot command',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'snapshot_period': {
                'type': 'string',
                'ui': {
                    'title': 'Snapshot period',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'snapshot_criteria': {
                'type': 'list',
                'ui': {
                    'title': 'Snapshot criteria',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ['w', 'c', 'u']
            },
            'snapshot_interval': {
                'type': 'integer',
                'ui': {
                    'title': 'Snapshot interval',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': 5
            },
            'obsess_over_service': {
                'type': 'boolean',
                'default': False
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
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
            # This to define if the object in this model are to be used in the UI
            'ui': {
                'type': 'boolean',
                'default': True,
                'required': False,
                # UI parameters for the objects
                'ui': {
                    'list_title': 'Services list (%d items)',
                    'page_title': 'Service: %s',
                    'uid': 'service_description',
                    'visible': True,
                    'orderable': True,
                    'searchable': True
                }
            }
        },
    }
