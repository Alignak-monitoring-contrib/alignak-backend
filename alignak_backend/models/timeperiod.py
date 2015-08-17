def get_name():
    return 'timeperiod'


def get_schema():
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': 'unknown'
            },

            'use': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'timeperiod',
                    'embeddable': True
                },
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

            'timeperiod_name': {
                'type': 'string',
            },

            'alias': {
                'type': 'string',
                'default': 'none'
            },

            'dateranges': {
                'type': 'list',
                'default': []
            },

            'exclude': {
                'type': 'list',
                'default': []
            },

            'is_active': {
                'type': 'boolean',
                'default': False
            },
        }
    }
