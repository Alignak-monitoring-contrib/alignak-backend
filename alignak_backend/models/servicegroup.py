def get_name():
    return 'servicegroup'


def get_schema():
    return {
        'schema': {
            'members': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                }
            },

            'servicegroup_members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'servicegroup',
                        'embeddable': True,
                    }
                },
            },

            'servicegroup_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'default': ''
            },

            'alias': {
                'type': 'string',
                'default': ''
            },

            'notes': {
                'type': 'string',
                'default': ''
            },

            'notes_url': {
                'type': 'string',
                'default': ''
            },

            'action_url': {
                'type': 'string',
                'default': ''
            },
        }
    }
