def get_name():
    return 'brotherhood'


def get_schema():
    return {
        'schema': {
            'name': {
                'type': 'string',
                'default': '',
                'required': True,
                'unique': True,
            },
        }
    }
