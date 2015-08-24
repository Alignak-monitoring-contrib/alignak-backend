def get_name():
    return 'liveservice'


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
                'unique': True,
            },
            'description': {
                'type': 'string',
                'default': None
            },
            'state': {
                'type': 'string',
                'default': 'OK',
                'allowed': ["OK", "WARNING", "CRITICAL", "UNKNOWN"]
            },
            'acknowledged': {
                'type': 'boolean',
                'default': False
            },
            'last_check': {
                'type': 'integer',
                'default': None
            },
            'last_state_change': {
                'type': 'integer',
                'default': None
            },
            'output': {
                'type': 'string',
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
