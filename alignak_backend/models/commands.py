def get_name():
    return 'commands'

def get_schema():
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': 'unknown'
            },

            'use': {
                'type': 'list',
                'default': None
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

            'command_name': {
                'type': 'string',
            },

            'command_line': {
                'type': 'string',
            },

            'poller_tag': {
                'type': 'string',
                'default': 'None'
            },

            'reactionner_tag': {
                'type': 'string',
                'default': 'None'
            },

            'module_type': {
                'type': 'string',
            },

            'timeout': {
                'type': 'integer',
                'default': -1
            },

            'enable_environment_macros': {
                'type': 'boolean',
                'default': False
            },
        }
    }


