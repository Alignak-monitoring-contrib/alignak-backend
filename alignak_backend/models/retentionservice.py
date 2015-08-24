def get_name():
    return 'retentionservice'


def get_schema():
    return {
        'allow_unknown': True,
        'schema': {
            'service': {
                'type': 'list',
            },
        }
    }
