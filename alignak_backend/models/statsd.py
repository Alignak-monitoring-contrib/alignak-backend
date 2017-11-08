#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Resource information of statsd.
statsd is used to send data to timeseries (graphite, influxdb) but not directly. We send to statsd
and after it send to the timeserie database. The goal is to have data all time in timeseries
databases when use passive checks for example (passive check = not have often the perfdata).
"""


def get_name(friendly=False):
    """Get name of this resource

    :return: name of this resource
    :rtype: str
    """
    if friendly:  # pragma: no cover
        return "StatsD connection"
    return 'statsd'


def get_doc():  # pragma: no cover
    """Get documentation of this resource

    :return: rst string
    :rtype: str
    """
    return """
    The ``statsd`` model contains information to provide the monitored system performance
    data to StatsD.

    The Alignak backend will use those information to connect to a StatsD daemon and send the
    timeseries data. StatsD may be used as a front-end to Graphite or InfluxDB thus an
    instance of this data model may be related to a Graphite or InfluxDB instance.
    """


def get_schema():
    """Schema structure of this resource

    :return: schema dictionary
    :rtype: dict
    """
    return {
        'schema': {
            'schema_version': {
                'type': 'integer',
                'default': 1,
            },
            'name': {
                'schema_version': 1,
                'title': 'StatsD connection name',
                'comment': 'Unique StatsD connection name',
                'type': 'string',
                'required': True,
                'empty': False,
                'unique': True,
            },
            'address': {
                'schema_version': 1,
                'title': 'Server address',
                'comment': '',
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'port': {
                'schema_version': 1,
                'title': 'Server port',
                'comment': '',
                'type': 'integer',
                'empty': False,
                'default': 8125
            },
            'prefix': {
                'schema_version': 1,
                'title': 'Metrics prefix',
                'comment': 'Prefix that is configured in the StatsD server (if any).',
                'type': 'string',
                'default': '',
            },

            # Realm
            '_realm': {
                'schema_version': 1,
                'title': 'Realm',
                'comment': 'Realm this element belongs to.',
                'type': 'objectid',
                'data_relation': {
                    'resource': 'realm',
                    'embeddable': True
                },
                'required': True,
            },
            '_sub_realm': {
                'schema_version': 1,
                'title': 'Sub-realms',
                'comment': 'Is this element visible in the sub-realms of its realm?',
                'type': 'boolean',
                'default': True
            },

            # Users CRUD permissions
            '_users_read': {
                'schema_version': 1,
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
                'schema_version': 1,
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
                'schema_version': 1,
                'type': 'list',
                'schema': {
                    'type': 'objectid',
                    'data_relation': {
                        'resource': 'user',
                        'embeddable': True,
                    }
                },
            },
        },
        'schema_deleted': {}
    }
