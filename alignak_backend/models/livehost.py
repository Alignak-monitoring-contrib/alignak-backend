def get_name():
    return 'livehost'


def get_schema():
    return {
        'schema': {
            'host_name': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'host',
                    'embeddable': True
                },
                'required': True,
                'unique': True,
            },
            'state': {
                'type': 'string',
                'default': 'UP',
                'allowed': ["UP", "DOWN", "UNREACHABLE"]
            },
            'state_type': {
                'type': 'string',
                'default': 'HARD',
                'allowed': ["HARD", "SOFT"]
            },
            'acknowledged': {
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'type': 'integer',
                'default': None
            },
            'output': {
                'type': 'string',
                'default': None
            },
            'long_output': {
                'type': 'string',
                'default': None
            },
            'perf_data': {
                'type': 'string',
                'default': None
            }
        }
    }
