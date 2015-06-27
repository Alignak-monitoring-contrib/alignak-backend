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


