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

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': 'unknown'
            },
            'name': {
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$',
                'dependencies': ['check_command']
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'alias': {
                'type': 'string',
                'default': ''
            },
            'customs': {
                'type': 'dict',
                'default': {}
            },
            'display_name': {
                'type': 'string',
                'default': ''
            },
            'address': {
                'type': 'string',
                'default': ''
            },
            'parents': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            'check_command': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                }
            },
            'check_command_args': {
                'type': 'string',
                'default': ''
            },
            'initial_state': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 1,
                'default': 'u',
                'allowed': ["o", "d", "u"]
            },
            'max_check_attempts': {
                'type': 'integer',
                'default': 1
            },
            'check_interval': {
                'type': 'integer',
                'default': 5
            },
            'retry_interval': {
                'type': 'integer',
                'default': 0
            },
            'active_checks_enabled': {
                'type': 'boolean',
                'default': True
            },
            'passive_checks_enabled': {
                'type': 'boolean',
                'default': True
            },
            'check_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'check_freshness': {
                'type': 'boolean',
                'default': False
            },
            'freshness_threshold': {
                'type': 'integer',
                'default': 0
            },
            'event_handler': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                },
                'nullable': True
            },
            'event_handler_enabled': {
                'type': 'boolean',
                'default': False
            },
            'low_flap_threshold': {
                'type': 'integer',
                'default': 25
            },
            'high_flap_threshold': {
                'type': 'integer',
                'default': 50
            },
            'flap_detection_enabled': {
                'type': 'boolean',
                'default': True
            },
            'flap_detection_options': {
                'type': 'list',
                'default': ['o', 'd', 'u'],
                'allowed': ['o', 'd', 'u']
            },
            'process_perf_data': {
                'type': 'boolean',
                'default': True
            },
            'users': {
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
            'usergroups': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'usergroup',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            'notification_interval': {
                'type': 'integer',
                'default': 60
            },
            'first_notification_delay': {
                'type': 'integer',
                'default': 0
            },
            'notification_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                }
            },
            'notification_options': {
                'type': 'list',
                'default': ['d', 'u', 'r', 'f', 's'],
                'allowed': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'notifications_enabled': {
                'type': 'boolean',
                'default': True
            },
            'stalking_options': {
                'type': 'list',
                'default': [],
                'allowed': ['o', 'd', 'u']
            },
            'notes': {
                'type': 'string',
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                'default': ''
            },
            'action_url': {
                'type': 'string',
                'default': ''
            },
            'icon_image': {
                'type': 'string',
                'default': ''
            },
            'icon_image_alt': {
                'type': 'string',
                'default': ''
            },
            'icon_set': {
                'type': 'string',
                'default': ''
            },
            'vrml_image': {
                'type': 'string',
                'default': ''
            },
            'statusmap_image': {
                'type': 'string',
                'default': ''
            },
            '2d_coords': {
                'type': 'string',
                'default': ''
            },
            '3d_coords': {
                'type': 'string',
                'default': ''
            },
            'failure_prediction_enabled': {
                'type': 'boolean',
                'default': False
            },
            'poller_tag': {
                'type': 'string',
                'default': 'None'
            },
            'reactionner_tag': {
                'type': 'string',
                'default': 'None'
            },
            'resultmodulations': {
                'type': 'list',
                'default': []
            },
            'business_impact_modulations': {
                'type': 'list',
                'default': []
            },
            'escalations': {
                'type': 'list',
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
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'nullable': True
            },
            'time_to_orphanage': {
                'type': 'integer',
                'default': 300
            },
            'service_overrides': {
                'type': 'list',
                'default': []
            },
            'service_excludes': {
                'type': 'list',
                'default': []
            },
            'service_includes': {
                'type': 'list',
                'default': []
            },
            'labels': {
                'type': 'list',
                'default': []
            },
            'business_rule_output_template': {
                'type': 'string',
                'default': ''
            },
            'business_rule_smart_notifications': {
                'type': 'boolean',
                'default': False
            },
            'business_rule_downtime_as_ack': {
                'type': 'boolean',
                'default': False
            },
            'business_rule_host_notification_options': {
                'type': 'list',
                'default': ['d', 'u', 'r', 'f', 's'],
                'allowed': ['d', 'u', 'r', 'f', 's', 'n']
            },
            'business_rule_service_notification_options': {
                'type': 'list',
                'default': ['w', 'u', 'c', 'r', 'f', 's'],
                'allowed': ['w', 'u', 'c', 'r', 'f', 's', 'n']
            },
            'business_impact': {
                'type': 'integer',
                'default': 2
            },
            'trigger': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'trigger',
                    'embeddable': True
                },
                'nullable': True
            },
            'trigger_broker_raise_enabled': {
                'type': 'boolean',
                'default': False
            },
            'trending_policies': {
                'type': 'list',
                'default': []
            },
            'checkmodulations': {
                'type': 'list',
                'default': []
            },
            'macromodulations': {
                'type': 'list',
                'default': []
            },
            'custom_views': {
                'type': 'list',
                'default': []
            },
            'snapshot_enabled': {
                'type': 'boolean',
                'default': False
            },
            'snapshot_command': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                },
                'nullable': True
            },
            'snapshot_period': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
                'nullable': True
            },
            'snapshot_criteria': {
                'type': 'list',
                'default': ['d', 'u']
            },
            'snapshot_interval': {
                'type': 'integer',
                'default': 5
            },
            'obsess_over_host': {
                'type': 'boolean',
                'default': False
            },
            'location': {
                'type': 'point',
                'default': {"type": "Point", "coordinates": [100.0, 10.0]}
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
                'default': False
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
            '_is_template': {
                'type': 'boolean',
                'default': False
            },
            '_templates': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
                'default': []
            },
            '_templates_with_services': {
                'type': 'boolean',
                'default': False
            },
            '_template_fields': {
                'type': 'list',
                'default': []
            },
        }
    }
