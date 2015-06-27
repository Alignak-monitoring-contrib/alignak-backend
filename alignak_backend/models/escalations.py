def get_name():
    return 'escalations'

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

            'escalation_name': {
                'type': 'string',
            },

            'first_notification': {
                'type': 'integer',
            },

            'last_notification': {
                'type': 'integer',
            },

            'first_notification_time': {
                'type': 'integer',
            },

            'last_notification_time': {
                'type': 'integer',
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
                'type': 'objectid',
                'data_relation': {
                     'resource': 'contacts',
                     'embeddable': True
                }
            },

            'contact_groups': {
                'type': 'objectid',
                'data_relation': {
                     'resource': 'contactgroups',
                     'embeddable': True
                }
            },
        }
    }


