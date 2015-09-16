#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Common schema part for resource schema
"""

def user_rights():
    return {
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

def contacts():
    return {
        'contacts': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True,
                }
            },
        }
    }

def contact_groups():
    return {
        'contact_groups': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'contactgroup',
                    'embeddable': True,
                }
            },
        }
    }