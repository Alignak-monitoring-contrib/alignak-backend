#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of brotherhood
"""

def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'brotherhood'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionnary
    :rtype: dict
    """
    return {
        'schema': {
            'name': {
                'type': 'string',
                'default': '',
                'required': True,
                'unique': True,
            },
        }
    }
