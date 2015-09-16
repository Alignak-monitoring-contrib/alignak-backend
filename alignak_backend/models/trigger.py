def get_name():
    return 'trigger'


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
                    'resource': 'trigger',
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
            'trigger_name': {
                'type': 'string',
            },
            'code_src': {
                'type': 'string',
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
