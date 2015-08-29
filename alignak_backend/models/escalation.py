def get_name():
    return 'escalation'


def get_schema():
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': ''
            },
            'use': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'escalation',
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
            'escalation_name': {
                'type': 'string',
                'default': ''
            },
            'first_notification': {
                'type': 'integer',
                'default': 0
            },
            'last_notification': {
                'type': 'integer',
                'default': 0
            },
            'first_notification_time': {
                'type': 'integer',
                'default': 0
            },
            'last_notification_time': {
                'type': 'integer',
                'default': 0
            },
            'notification_interval': {
                'type': 'integer',
                'default': -1
            },
            'escalation_period': {
                'type': 'string',
                'default': ''
            },
            'escalation_options': {
                'type': 'list',
                'default': ['d', 'u', 'r', 'w', 'c']
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
        }
    }
