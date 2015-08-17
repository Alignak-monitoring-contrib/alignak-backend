def get_name():
    return 'trigger'


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
                    'resource': 'trigger',
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

            'trigger_name': {
                'type': 'string',
            },

            'code_src': {
                'type': 'string',
            },
        }
    }
