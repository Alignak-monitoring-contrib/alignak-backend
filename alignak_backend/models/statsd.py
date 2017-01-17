#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of statsd.
statsd is used to send data to timeseries (graphite, influxdb) but not directly. We send to statsd
and after it send to the timeserie database. The goal is to have data all time in timeseries
databases when use passive checks for example (passive check = not have often the perfdata).
"""


def get_name():
    """
    Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    return 'statsd'


def get_schema():
    """
    Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'name': {
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
            },
            'address': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'port': {
                'type': 'integer',
                'empty': False,
                'default': 8125
            },
            'prefix': {
                'type': 'string',
                'default': '',
            },
            '_realm': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'type': 'boolean',
                'default': False
            },
            '_users_read': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
            '_users_update': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
            '_users_delete': {
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                }
            }
        }
    }
