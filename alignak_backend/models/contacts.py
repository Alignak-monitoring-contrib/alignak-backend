def get_name():
    return 'contacts'


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

            'contact_name': {
                'type': 'string',
            },

            'alias': {
                'type': 'string',
                'default': 'none'
            },

            'contactgroups': {
                'type': 'list',
                'default': []
            },

            'host_notifications_enabled': {
                'type': 'boolean',
                'default': True
            },

            'service_notifications_enabled': {
                'type': 'boolean',
                'default': True
            },

            'host_notification_period': {
                'type': 'string',
            },

            'service_notification_period': {
                'type': 'string',
            },

            'host_notification_options': {
                'type': 'list',
                'default': []
            },

            'service_notification_options': {
                'type': 'list',
                'default': []
            },

            'host_notification_commands': {
                'type': 'list',
                'default': []
            },

            'service_notification_commands': {
                'type': 'list',
                'default': []
            },

            'min_business_impact': {
                'type': 'integer',
                'default': 0
            },

            'email': {
                'type': 'string',
                'default': 'none'
            },

            'pager': {
                'type': 'string',
                'default': 'none'
            },

            'address1': {
                'type': 'string',
                'default': 'none'
            },

            'address2': {
                'type': 'string',
                'default': 'none'
            },

            'address3': {
                'type': 'string',
                'default': 'none'
            },

            'address4': {
                'type': 'string',
                'default': 'none'
            },

            'address5': {
                'type': 'string',
                'default': 'none'
            },

            'address6': {
                'type': 'string',
                'default': 'none'
            },

            'can_submit_commands': {
                'type': 'boolean',
                'default': False
            },

            'is_admin': {
                'type': 'boolean',
                'default': False
            },

            'expert': {
                'type': 'boolean',
                'default': False
            },

            'retain_status_information': {
                'type': 'boolean',
                'default': True
            },

            'notificationways': {
                'type': 'list',
                'default': []
            },

            'password': {
                'type': 'string',
                'default': 'NOPASSWORDSET'
            },
        }
    }
