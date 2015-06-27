def get_name():
    return 'serviceextinfos'


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
