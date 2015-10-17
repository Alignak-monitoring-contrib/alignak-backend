#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of hostgroup
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'hostgroup'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'host',
                        'embeddable': True,
                    }
                },
                'ui': {
                    'title': 'Members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
            },
            'hostgroup_members': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'hostgroup',
                        'embeddable': True,
                    }
                },
                'ui': {
                    'title': 'Hosts groups members',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
            },
            'hostgroup_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'default': '',
                'ui': {
                    'title': 'Name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
            },
            'alias': {
                'type': 'string',
                'default': '',
                'ui': {
                    'title': 'Alias',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },
            },
            'notes': {
                'type': 'string',
                'default': '',
                'ui': {
                    'title': 'Notes',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },

            },
            'notes_url': {
                'type': 'string',
                'default': '',
                'ui': {
                    'title': 'Notes (URL)',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },

            },
            'action_url': {
                'type': 'string',
                'default': '',
                'ui': {
                    'title': 'Action (URL)',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },

            },
            'realm': {
                'type': 'string',
                'default': None,
                'ui': {
                    'title': 'Realm',
                    'visible': True,
                    'orderable': True,
                    'searchable': True,
                    "format": None
                },

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
            # This to define if the object in this model are to be used in the UI
            'ui': {
                'type': 'boolean',
                'default': True,
                'required': False,
                # UI parameters for the objects
                'ui': {
                    'list_title': 'Hosts groups list (%d items)',
                    'page_title': 'Host group: %s',
                    'uid': 'hostgroup_name',
                    'visible': True,
                    'orderable': True,
                    'searchable': True
                }
            }
        }
    }
