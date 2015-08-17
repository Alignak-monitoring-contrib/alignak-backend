def get_name():
    return 'servicedependency'


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
                    'resource': 'servicedependency',
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



            'dependent_host_name': {
                'type': 'string'
            },

            'dependent_hostgroup_name': {
                'type': 'string',
                'default': ''
            },


            'dependent_service_description': {
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

            'explode_hostgroup': {
                'type': 'boolean',
                'default': False
            },
        }
    }
