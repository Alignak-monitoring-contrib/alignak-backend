def get_name():
    return 'services'

def get_schema():
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': 'unknown'
            },

            'use': {
                'type': 'list',
                'default': None
            },

            'name': {
                'type': 'string',
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
                'type': 'string',
            },

            'hostgroup_name': {
                'type': 'string',
            },

            'service_description': {
                'type': 'string',
            },

            'display_name': {
                'type': 'string',
            },

            'servicegroups': {
                'type': 'list',
                'default': []
            },

            'is_volatile': {
                'type': 'boolean',
                'default': False
            },

            'check_command': {
                'type': 'string',
            },

            'initial_state': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 1,
                'default': 'o'
            },

            'max_check_attempts': {
                'type': 'integer',
                'default': 1
            },

            'check_interval': {
                'type': 'integer',
                'default': 0
            },

            'retry_interval': {
                'type': 'integer'
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
                'type': 'string',
            },

            'obsess_over_host': {
                'type': 'boolean',
                'default': False
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
                'type': 'string',
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
                'type': 'string'
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
                'type': 'objectid',
                'data_relation': {
                     'resource': 'users',
                     'embeddable': True
                }
            },

            'contact_groups': {
                'type': 'objectid',
                'data_relation': {
                     'resource': 'contact_groups',
                     'embeddable': True
                }
            },

            'stalking_options': {
                'type': 'list',
                'default': []
            },

            'notes': {
                'type': 'string'
            },

            'notes_url': {
                'type': 'string'
            },

            'action_url': {
                'type': 'string'
            },

            'icon_image': {
                'type': 'string'
            },

            'icon_image_alt': {
                'type': 'string'
            },

            'icon_set': {
                'type': 'string'
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
                'default': []
            },

            'maintenance_period': {
                'type': 'string'
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
                'default': []
            },

            'duplicate_foreach': {
                'type': 'string'
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
                'type': 'string'
            },

            'trigger_name': {
                'type': 'string'
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
                'type': 'string'
            },

            'snapshot_period': {
                'type': 'string'
            },

            'snapshot_criteria': {
                'type': 'list',
                'default': ['w', 'c', 'u']
            },

            'snapshot_interval': {
                'type': 'integer',
                'default': 5
            }
        }
    }


