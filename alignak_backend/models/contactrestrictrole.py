def get_name():
    return 'contactrestrictrole'


def get_schema():
    return {
        'schema': {
            'contact': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
                'required': True,
            },
            'brotherhood': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'brotherhood',
                    'embeddable': True
                },
                'required': True,
            },
            'resource': {
                'type': 'list',
                'default': [],
                'required': True,
            },
        }
    }
