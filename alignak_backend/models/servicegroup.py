#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of servicegroup
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'servicegroup'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'members': {
                'type': 'list',
                'ui': {
                    'title': 'Members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'service',
                        'embeddable': True,
                    }
                },
            },
            'servicegroup_members': {
                'type': 'list',
                'ui': {
                    'title': 'Servicegroup members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'servicegroup',
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
                    "format": None
                },
                'required': True,
                'empty': False,
                'unique': True,
                'default': ''
            },
            'alias': {
                'type': 'string',
                'ui': {
                    'title': 'Alias',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'notes': {
                'type': 'string',
                'ui': {
                    'title': 'Notes',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                'ui': {
                    'title': 'URL of notes',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
                'default': ''
            },
            'action_url': {
                'type': 'string',
                'ui': {
                    'title': 'URL of action',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
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
                    "format": None
                },
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
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
