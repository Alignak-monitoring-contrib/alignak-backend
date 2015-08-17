def get_name():
    return 'contactgroup'


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

            'unknown_members': {
                'type': 'list',
                'default': None
            },

            'id': {
                'type': 'integer',
                'default': 0
            },

            'contactgroup_name': {
                'type': 'string',
            },

            'alias': {
                'type': 'string',
            },
        }
    }
