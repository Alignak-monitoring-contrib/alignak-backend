def get_name():
    return 'timeperiod'


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
                    'resource': 'timeperiod',
                    'embeddable': True
                },
            },
            'name': {
                'type': 'string',
                'default': ''
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'register': {
                'type': 'boolean',
                'default': True
            },
            'timeperiod_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'default': ''
            },
            'alias': {
                'type': 'string',
                'default': ''
            },
            'dateranges': {
                'type': 'list',
                'default': []
            },
            'exclude': {
                'type': 'list',
                'default': []
            },
            'is_active': {
                'type': 'boolean',
                'default': False
            },
            '_brotherhood': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'brotherhood',
                        'embeddable': True,
                    }
                },
            },
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
    }
