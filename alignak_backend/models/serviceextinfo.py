def get_name():
    return 'serviceextinfo'


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
                    'resource': 'serviceextinfo',
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

            'host_name': {
                'type': 'string',
            },

            'service_description': {
                'type': 'string',
            },

            'notes': {
                'type': 'string'
            },

            'notes_url': {
                'type': 'string'
            },

            'icon_image': {
                'type': 'string'
            },

            'icon_image_alt': {
                'type': 'string'
            },
        }
    }
