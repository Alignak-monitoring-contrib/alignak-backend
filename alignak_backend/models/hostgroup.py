def get_name():
    return 'hostgroup'


def get_schema():
    return {
        'schema': {
            'members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
            },

            'hostgroup_members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
            },

            'hostgroup_name': {
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

            'realm': {
                'type': 'string',
                'default': None
            },
        }
    }
