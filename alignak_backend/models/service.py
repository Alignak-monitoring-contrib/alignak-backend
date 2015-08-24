def get_name():
    return 'service'


def get_schema():
    return {
        'allow_unknown': True,
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': ''
            },

            'use': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
            },

            'name': {
                'type': 'string',
                'default': ''
            },

            'definition_order': {
                'type': 'integer',
                'default': 100
            },

            'register': {
                'type': 'boolean',
                'default': True
            },

            'host_name': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
            },

            'hostgroup_name': {
                'type': 'string',
                'default': ''
            },

            'service_description': {
                'type': 'string',
                'regex': '^[^`~!$%^&*"|\'<>?,()=]+$',
                'dependencies': ['host_name', 'check_command']
            },

            'display_name': {
                'type': 'string',
                'default': ''
            },

            'servicegroups': {
                'type': 'list',
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
                'default': False
            },

            'check_command': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'command',
                    'embeddable': True
                },
                'allowed': ['bp_rule'],
                'nullable': True
            },

            'check_command_args': {
                'type': 'string',
                'default': ''
            },

            'initial_state': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 1,
                'default': 'o',
                'allowed': ["o", "w", "c", "u"]
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

            #'obsess_over_host': {
            #    'type': 'boolean',
            #    'default': False
            #},

            'check_freshness': {
                'type': 'boolean',
                'default': False
            },

            'freshness_threshold': {
                'type': 'integer',
                'default': 0
            },

            'event_handler': {
                'type': 'string',
                'default': ''
            },

            'event_handler_enabled': {
                'type': 'boolean',
                'default': False
            },

            'low_flap_threshold': {
                'type': 'integer',
                'default': -1
            },

            'high_flap_threshold': {
                'type': 'integer',
                'default': -1
            },

            'flap_detection_enabled': {
                'type': 'boolean',
                'default': True
            },

            'flap_detection_options': {
                'type': 'list',
                'default': ['o', 'w', 'c', 'u']
            },

            'process_perf_data': {
                'type': 'boolean',
                'default': True
            },

            'retain_status_information': {
                'type': 'boolean',
                'default': True
            },

            'retain_nonstatus_information': {
                'type': 'boolean',
                'default': True
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
                'default': ['w', 'u', 'c', 'r', 'f', 's']
            },

            'notifications_enabled': {
                'type': 'boolean',
                'default': True
            },

            'contacts': {
                'type': 'list',
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
                'default': []
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

            'failure_prediction_enabled': {
                'type': 'boolean',
                'default': False
            },

            'parallelize_check': {
                'type': 'boolean',
                'default': True
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
                }
            },

            'time_to_orphanage': {
                'type': 'integer',
                'default': 300
            },

            'merge_host_contacts': {
                'type': 'boolean',
                'default': False
            },

            'labels': {
                'type': 'list',
                'default': []
            },

            'host_dependency_enabled': {
                'type': 'boolean',
                'default': True
            },

            'business_rule_output_template': {
                'type': 'string'
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
                'default': []
            },

            'business_rule_service_notification_options': {
                'type': 'list',
                'default': []
            },

            'service_dependencies': {
                'type': 'list',
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
                'default': ''
            },

            'default_value': {
                'type': 'string',
                'default': []
            },

            'business_impact': {
                'type': 'integer',
                'default': 2
            },

            'trigger': {
                'type': 'string',
                'default': ''
            },

            'trigger_name': {
                'type': 'string',
                'default': ''
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

            'aggregation': {
                'type': 'string',
                'default': ''
            },

            'snapshot_enabled': {
                'type': 'boolean',
                'default': False
            },

            'snapshot_command': {
                'type': 'string',
                'default': ''
            },

            'snapshot_period': {
                'type': 'string',
                'default': ''
            },

            'snapshot_criteria': {
                'type': 'list',
                'default': ['w', 'c', 'u']
            },

            'snapshot_interval': {
                'type': 'integer',
                'default': 5
            }
        },
    }
