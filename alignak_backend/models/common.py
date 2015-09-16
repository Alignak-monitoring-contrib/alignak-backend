def user_rights():
    return {
        '_users_read': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True,
                }
            },
        },
        '_users_create': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True,
                }
            },
        },
        '_users_update': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True,
                }
            },
        },
        '_users_delete': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True,
                }
            },
        },
    }
