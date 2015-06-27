def get_name():
    return 'hosts'


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

            'alias': {
                'type': 'string',
            },

            'display_name': {
                'type': 'string',
            },

            'address': {
                'type': 'string',
            },

            'parents': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'hosts',
                    'embeddable': True
                }
            },

            'hostgroups': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'hostgroups',
                    'embeddable': True
                }
            },

            'check_command': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'commands',
                    'embeddable': True
                }
            },

            'initial_state': {
                'type': 'string',
                'minlength': 1,
                'maxlength': 1,
                'default': 'u'
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
                'default': 25
            },

            'low_flap_threshold': {
                'type': 'integer',
                'default': 50
            },

            'flap_detection_enabled': {
                'type': 'boolean',
                'default': True
            },

            'flap_detection_options': {
                'type': 'list',
                'default': ['o', 'd', 'u']
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
                'default': ['d', 'u', 'r', 'f']
            },

            'notifications_enabled': {
                'type': 'boolean',
                'default': True
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

            'vrml_image': {
                'type': 'string'
            },

            'statusmap_image': {
                'type': 'string'
            },

            '2d_coords': {
                'type': 'string'
            },

            '3d_coords': {
                'type': 'string'
            },

            'failure_prediction_enabled': {
                'type': 'boolean',
                'default': False
            },

            'realm': {
                'type': 'string'
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
                'default': ['d', 'u']
            },

            'snapshot_interval': {
                'type': 'integer',
                'default': 5
            }
        }
    }
