def get_name():
    return 'hostextinfo'


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
                    'resource': 'hostextinfo',
                    'embeddable': True
                },
            },

            'name': {
                'type': 'string',
                'default' : ''
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
                'required': True,
                'unique': True,
                'default' : ''
            },

            'notes': {
                'type': 'string',
                'default' : ''
            },

            'notes_url': {
                'type': 'string',
                'default' : ''
            },

            'icon_image': {
                'type': 'string',
                'default' : ''
            },

            'icon_image_alt': {
                'type': 'string',
                'default' : ''
            },

            'vrml_image': {
                'type': 'string',
                'default' : ''
            },

            'statusmap_image': {
                'type': 'string',
                'default' : ''
            },

            '2d_coords': {
                'type': 'string',
                'default' : ''
            },

            '3d_coords': {
                'type': 'string',
                'default' : ''
            },
        }
    }
