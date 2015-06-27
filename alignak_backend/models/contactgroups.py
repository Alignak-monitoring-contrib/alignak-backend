def get_name():
    return 'contactgroups'


def get_schema():
    return {
        'schema': {
            'members': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contacts',
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
