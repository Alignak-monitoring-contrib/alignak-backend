#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of retentionhost
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "Host data retention"
    return 'retentionhost'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``retentionhost`` model is used by the Alignak backend scheduler module for the
    Alignak retention feature.
    """


def get_schema():
    """Schema structure of this resource

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
