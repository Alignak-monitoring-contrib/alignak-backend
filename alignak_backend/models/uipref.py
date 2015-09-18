#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of host
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'uipref'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'contact': {
                'type': 'objectid',
                '_title': 'Contact',
                'data_relation': {
                    'resource': 'contact',
                    'embeddable': True
                },
                'required': True,
            },
        }
    }
