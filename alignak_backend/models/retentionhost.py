def get_name():
    return 'retentionhost'


def get_schema():
    return {
        'allow_unknown': True,
        'schema': {
            'host': {
                'type': 'string',
            },
        }
    }
