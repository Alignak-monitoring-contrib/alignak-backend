def get_name():
    return 'contactgroup'


def get_schema():
    return {
        'schema': {
            'members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            'contactgroup_members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
            },
            'contactgroup_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'default': ''
            },
            'alias': {
                'type': 'string',
                'default': ''
            },
        }
    }
