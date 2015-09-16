def get_name():
    return 'hostdependency'


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
                    'resource': 'hostdependency',
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
            'dependent_host_name': {
                'type': 'string',
                'default': ''
            },
            'dependent_hostgroup_name': {
                'type': 'string',
                'default': ''
            },
            'host_name': {
                'type': 'string'
            },
            'hostgroup_name': {
                'type': 'string',
                'default': 'unknown'
            },
            'inherits_parent': {
                'type': 'boolean',
                'default': False
            },
            'execution_failure_criteria': {
                'type': 'list',
                'default': ['n']
            },
            'notification_failure_criteria': {
                'type': 'list',
                'default': ['n']
            },
            'dependency_period': {
                'type': 'string',
                'default': ''
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
