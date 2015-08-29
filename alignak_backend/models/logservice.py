def get_name():
    return 'logservice'


def get_schema():
    return {
        'schema': {
            'service_description': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'service',
                    'embeddable': True
                },
                'required': True,
            },
            'state': {
                'type': 'string',
                'default': 'UP',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN"]
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
