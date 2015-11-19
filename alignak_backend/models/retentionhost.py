#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of retentionhost
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'retentionhost'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'allow_unknown': True,
        'schema': {
            'host': {
                'type': 'string',
            },
        }
    }
