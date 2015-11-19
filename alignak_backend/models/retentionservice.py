#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of retentionservice
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'retentionservice'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'service': {
                'type': 'list',
            },
        }
    }
