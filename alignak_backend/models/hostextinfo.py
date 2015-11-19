#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of hostextinfo
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'hostextinfo'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'imported_from': {
                'type': 'string',
                'default': ''
            },
            'name': {
                'type': 'string',
                'required': True,
                'unique': True,
            },
            'definition_order': {
                'type': 'integer',
                'default': 100
            },
            'host_name': {
                'type': 'string',
                'required': True,
                'unique': True,
                'default': ''
            },
            'notes': {
                'type': 'string',
                'default': ''
            },
            'notes_url': {
                'type': 'string',
                'default': ''
            },
            'icon_image': {
                'type': 'string',
                'default': ''
            },
            'icon_image_alt': {
                'type': 'string',
                'default': ''
            },
            'vrml_image': {
                'type': 'string',
                'default': ''
            },
            'statusmap_image': {
                'type': 'string',
                'default': ''
            },
            '2d_coords': {
                'type': 'string',
                'default': ''
            },
            '3d_coords': {
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
