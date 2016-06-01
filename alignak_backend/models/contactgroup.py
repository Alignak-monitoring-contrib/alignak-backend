#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of contactgroup
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'contactgroup'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        # 'allow_unknown': True,
        'schema': {
            # 'uuid': {
            # 'type': 'string',
            # 'required': True,
            # 'empty': False,
            # 'unique': True
            # },

            'members': {
                'type': 'list',
                'ui': {
                    'title': 'Contact members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contact',
                        'embeddable': True,
                    }
                },
            },
            'contactgroup_members': {
                'type': 'list',
                'ui': {
                    'title': 'Contactgroup members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'contactgroup',
                        'embeddable': True,
                    }
                },
            },
            'name': {
                'type': 'string',
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'required': True,
                'empty': False,
                'unique': True
            },
            'definition_order': {
                'type': 'integer',
                'ui': {
                    'title': 'Definition order',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': 100
            },
            'alias': {
                'type': 'string',
                'ui': {
                    'title': 'Alias',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': ''
            },
            '_realm': {
                'type': 'objectid',
                'ui': {
                    'title': 'Realm',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'type': 'boolean',
                'ui': {
                    'title': 'Readable on sub realms',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    'format': None
                },
                'default': False
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
                'default': [],
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
                'default': [],
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
                'default': [],
            },
        }
    }
